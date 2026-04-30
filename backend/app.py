"""Flask API backend for the Morse Code Telegraph Translator."""

import base64
import hmac
import logging
import os
import time
import uuid

import numpy as np
from dotenv import load_dotenv
from flask import Flask, g, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from ml_model import get_tap_detector
from morse import decode_morse, encode_text
from signal_processor import AdaptiveThreshold, classify_signal

# Load .env before reading any env vars.
# Use a path relative to this file so imports work from any cwd.
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


def _is_truthy(value: str) -> bool:
    return value.lower() in ("1", "true", "yes", "on")


app = Flask(__name__)

# Global app configuration
app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_CONTENT_LENGTH", str(5 * 1024 * 1024)))

# CORS — locked to origins listed in CORS_ORIGINS (space-separated).
_raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173 http://localhost:8080")
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split() if o.strip()]
CORS(app, origins=ALLOWED_ORIGINS, supports_credentials=False)

# Logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

# Rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=[os.getenv("GLOBAL_RATE_LIMIT", "120 per minute")],
    storage_uri=os.getenv("RATE_LIMIT_STORAGE_URI", "memory://"),
)

# Security configuration
API_AUTH_ENABLED = _is_truthy(os.getenv("API_AUTH_ENABLED", "true"))
API_SHARED_KEY = os.getenv("API_SHARED_KEY", "change-me-in-production")
FLASK_ENV = os.getenv("FLASK_ENV", "production")

if API_AUTH_ENABLED and FLASK_ENV == "production" and API_SHARED_KEY == "change-me-in-production":
    raise RuntimeError("API_SHARED_KEY must be configured in production when API_AUTH_ENABLED=true")

# Configuration
MAX_AUDIO_LENGTH = int(os.getenv("MAX_AUDIO_LENGTH", "30"))  # seconds
MAX_TEXT_LENGTH = 500  # characters — prevent oversized encode/decode requests
SAMPLE_RATE = 44100
UPLOAD_FOLDER = "uploads"
JSON_ENDPOINTS = {"/api/decode", "/api/encode", "/api/process-signal"}
AUTH_EXEMPT_ENDPOINTS = {"/api/health"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global state
adaptive_threshold = AdaptiveThreshold()
tap_detector = get_tap_detector()


@app.before_request
def before_request() -> tuple | None:
    g.request_id = str(uuid.uuid4())
    g.request_start = time.perf_counter()

    if not request.path.startswith("/api"):
        return None

    # Enforce JSON content type for JSON endpoints.
    if request.method in ("POST", "PUT", "PATCH") and request.path in JSON_ENDPOINTS and not request.is_json:
        return jsonify({"error": "Content-Type must be application/json", "request_id": g.request_id}), 415

    # API-key authentication for API routes, except health check.
    if API_AUTH_ENABLED and request.path not in AUTH_EXEMPT_ENDPOINTS:
        provided_key = request.headers.get("X-API-Key", "")
        if not hmac.compare_digest(provided_key, API_SHARED_KEY):
            return jsonify({"error": "Unauthorized", "request_id": g.request_id}), 401

    return None


@app.after_request
def after_request(response):
    request_id = getattr(g, "request_id", "")
    duration_ms = (time.perf_counter() - getattr(g, "request_start", time.perf_counter())) * 1000

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"

    # HSTS should only be enabled when served over HTTPS.
    if _is_truthy(os.getenv("ENABLE_HSTS", "false")):
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    app.logger.info(
        "request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
        request_id,
        request.method,
        request.path,
        response.status_code,
        duration_ms,
    )
    return response


# ─────────────────────────────────────────────────────────────
# Health & Status
# ─────────────────────────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
@limiter.exempt
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "model_trained": tap_detector.is_trained,
        "sample_rate": SAMPLE_RATE
    })


# ─────────────────────────────────────────────────────────────
# Morse Dictionary & Encoding
# ─────────────────────────────────────────────────────────────

@app.route("/api/decode", methods=["POST"])
@limiter.limit("60 per minute")
def api_decode():
    """Decode Morse code to text.
    
    Request body:
        {
            "morse": "... --- ...",
            "morse_chars": ["...", "---", "..."]  (alternative)
        }
    """
    data = request.get_json(silent=True) or {}

    if "morse_chars" in data:
        chars = data["morse_chars"]
        if not isinstance(chars, list) or len(chars) > MAX_TEXT_LENGTH:
            return jsonify({"error": "'morse_chars' must be a list of at most 500 items"}), 400
        result = "".join(decode_morse(char) for char in chars)
    elif "morse" in data:
        morse_str = data["morse"].strip()
        if len(morse_str) > MAX_TEXT_LENGTH * 6:  # rough upper bound
            return jsonify({"error": "'morse' input too long"}), 400
        result = "".join(decode_morse(char) for char in morse_str.split())
    else:
        return jsonify({"error": "Missing 'morse' or 'morse_chars'"}), 400
    
    return jsonify({"decoded": result})


@app.route("/api/encode", methods=["POST"])
@limiter.limit("60 per minute")
def api_encode():
    """Encode text to Morse code.
    
    Request body:
        {
            "text": "HELLO"
        }
    """
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")

    if not text or not text.strip():
        return jsonify({"error": "Missing 'text'"}), 400
    if len(text) > MAX_TEXT_LENGTH:
        return jsonify({"error": f"'text' exceeds maximum length of {MAX_TEXT_LENGTH} characters"}), 400

    morse_code = encode_text(text)
    return jsonify({"morse_code": morse_code})


# ─────────────────────────────────────────────────────────────
# Calibration
# ─────────────────────────────────────────────────────────────

@app.route("/api/calibrate", methods=["POST"])
@limiter.limit("5 per minute")
def api_calibrate():
    """Train the ML model on background noise and tap samples.
    
    Request body (multipart/form-data):
        - background: WAV file (5 seconds of silence)
        - taps: WAV file (5 seconds of table taps)
    """
    if "background" not in request.files or "taps" not in request.files:
        return jsonify({"error": "Missing 'background' or 'taps' files"}), 400
    
    try:
        # Load audio files
        bg_file = request.files["background"]
        tap_file = request.files["taps"]
        
        # For now, assume 16-bit PCM WAV
        # In production, use librosa or soundfile
        bg_audio = np.frombuffer(bg_file.read(), dtype=np.int16).astype(np.float32) / 32768.0
        tap_audio = np.frombuffer(tap_file.read(), dtype=np.int16).astype(np.float32) / 32768.0
        
        # Apply gain
        bg_audio *= 100
        tap_audio *= 100

        if len(bg_audio) / SAMPLE_RATE > MAX_AUDIO_LENGTH or len(tap_audio) / SAMPLE_RATE > MAX_AUDIO_LENGTH:
            return jsonify({"error": f"Audio exceeds max length of {MAX_AUDIO_LENGTH}s", "request_id": g.request_id}), 400
        
        # Train
        accuracy = tap_detector.train(bg_audio, tap_audio)
        
        return jsonify({
            "status": "trained",
            "accuracy": float(accuracy),
            "samples_bg": len(bg_audio),
            "samples_tap": len(tap_audio)
        })
    
    except Exception:
        app.logger.exception("calibrate_failed request_id=%s", g.request_id)
        return jsonify({"error": "Calibration failed", "request_id": g.request_id}), 500


@app.route("/api/calibrate-status", methods=["GET"])
@limiter.limit("30 per minute")
def calibrate_status():
    """Check if the model is trained."""
    return jsonify({
        "is_trained": tap_detector.is_trained,
        "model_type": "RandomForest" if tap_detector.is_trained else "None"
    })


# ─────────────────────────────────────────────────────────────
# Mic Audio Processing
# ─────────────────────────────────────────────────────────────

@app.route("/api/classify-tap", methods=["POST"])
@limiter.limit("90 per minute")
def api_classify_tap():
    """Classify a single audio frame as tap or noise.
    
    Request body (JSON):
        {
            "audio": [base64 encoded audio data],
            "sample_rate": 44100  (optional)
        }
    
    Or (multipart/form-data):
        - audio_file: WAV file
    """
    try:
        if "audio_file" in request.files:
            # WAV file upload
            audio_file = request.files["audio_file"]
            audio_data = np.frombuffer(audio_file.read(), dtype=np.int16).astype(np.float32) / 32768.0
        else:
            # JSON with base64
            data = request.get_json(silent=True) or {}
            audio_b64 = data.get("audio", "")
            if not audio_b64:
                return jsonify({"error": "Missing audio data"}), 400
            audio_bytes = base64.b64decode(audio_b64)
            audio_data = np.frombuffer(audio_bytes, dtype=np.float32)

        if len(audio_data) / SAMPLE_RATE > MAX_AUDIO_LENGTH:
            return jsonify({"error": f"Audio exceeds max length of {MAX_AUDIO_LENGTH}s", "request_id": g.request_id}), 400
        
        # Get ML prediction
        if tap_detector.is_trained:
            tap_prob, is_tap = tap_detector.predict(audio_data)
        else:
            tap_prob, is_tap = 0.0, False
        
        # Classify as dot or dash based on duration
        # For this endpoint, we assume the entire frame is one signal
        duration = len(audio_data) / SAMPLE_RATE
        signal_type = classify_signal(duration)
        
        return jsonify({
            "tap_probability": float(tap_prob),
            "is_tap": bool(is_tap),
            "signal_type": signal_type,
            "duration_ms": float(duration * 1000),
            "model_trained": tap_detector.is_trained
        })
    
    except Exception:
        app.logger.exception("classify_tap_failed request_id=%s", g.request_id)
        return jsonify({"error": "Audio classification failed", "request_id": g.request_id}), 500


@app.route("/api/process-signal", methods=["POST"])
@limiter.limit("90 per minute")
def api_process_signal():
    """Process a complete signal (press duration) to classify as dot, dash, or reject.
    
    Request body (JSON):
        {
            "duration_ms": 250,        # Press duration in milliseconds
            "audio": [...],            # Optional: audio frame for ML validation
            "use_ml": true             # Whether to validate with ML model
        }
    """
    data = request.get_json(silent=True) or {}
    duration_ms = data.get("duration_ms", 0)
    use_ml = data.get("use_ml", tap_detector.is_trained)

    try:
        duration_ms = float(duration_ms)
    except (TypeError, ValueError):
        return jsonify({"error": "'duration_ms' must be a number", "request_id": g.request_id}), 400

    if duration_ms <= 0 or duration_ms > MAX_AUDIO_LENGTH * 1000:
        return jsonify({"error": "'duration_ms' is out of allowed range", "request_id": g.request_id}), 400
    
    duration_s = duration_ms / 1000.0
    signal_type = classify_signal(duration_s)
    
    validation_result = {
        "valid": True,
        "reason": "No ML validation"
    }
    
    # Optional ML validation
    if use_ml and tap_detector.is_trained and "audio" in data:
        try:
            audio_b64 = data["audio"]
            audio_bytes = base64.b64decode(audio_b64)
            audio_data = np.frombuffer(audio_bytes, dtype=np.float32)
            if len(audio_data) / SAMPLE_RATE > MAX_AUDIO_LENGTH:
                return jsonify({"error": f"Audio exceeds max length of {MAX_AUDIO_LENGTH}s", "request_id": g.request_id}), 400
            tap_prob, is_tap = tap_detector.predict(audio_data)
            validation_result["valid"] = is_tap
            validation_result["reason"] = f"ML validation: {tap_prob:.0%} confidence"
        except Exception:
            validation_result["valid"] = False
            validation_result["reason"] = "ML validation failed"
    
    return jsonify({
        "signal_type": signal_type if validation_result["valid"] else None,
        "duration_ms": duration_ms,
        "validation": validation_result,
        "model_trained": tap_detector.is_trained
    })


# ─────────────────────────────────────────────────────────────
# Settings
# ─────────────────────────────────────────────────────────────

@app.route("/api/settings", methods=["GET"])
@limiter.limit("30 per minute")
def get_settings():
    """Get current signal processing settings."""
    return jsonify({
        "dot_threshold_ms": 150,
        "letter_gap_ms": 400,
        "word_gap_ms": 1000,
        "gain": 100,
        "spike_factor": 3.0,
        "sample_rate": SAMPLE_RATE
    })


# ─────────────────────────────────────────────────────────────
# Error Handling
# ─────────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(error):
    request_id = getattr(g, "request_id", "")
    return jsonify({"error": "Endpoint not found", "request_id": request_id}), 404


@app.errorhandler(500)
def internal_error(error):
    request_id = getattr(g, "request_id", "")
    return jsonify({"error": "Internal server error", "request_id": request_id}), 500


@app.errorhandler(413)
def payload_too_large(error):
    request_id = getattr(g, "request_id", "")
    return jsonify({"error": "Payload too large", "request_id": request_id}), 413


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
    # Dev server only — use gunicorn for production:
    #   gunicorn -c gunicorn.conf.py app:app
    app.run(host="0.0.0.0", port=port, debug=debug)
