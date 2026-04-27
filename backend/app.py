"""Flask API backend for the Morse Code Telegraph Translator."""

import os
import io
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

from morse import decode_morse, encode_text
from signal_processor import classify_signal, extract_features, AdaptiveThreshold
from ml_model import get_tap_detector

app = Flask(__name__)
CORS(app)

# Configuration
MAX_AUDIO_LENGTH = 30  # seconds
SAMPLE_RATE = 44100
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global state
adaptive_threshold = AdaptiveThreshold()
tap_detector = get_tap_detector()


# ─────────────────────────────────────────────────────────────
# Health & Status
# ─────────────────────────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
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
def api_decode():
    """Decode Morse code to text.
    
    Request body:
        {
            "morse": "... --- ...",
            "morse_chars": ["...", "---", "..."]  (alternative)
        }
    """
    data = request.get_json()
    
    if "morse_chars" in data:
        result = "".join(decode_morse(char) for char in data["morse_chars"])
    elif "morse" in data:
        morse_str = data["morse"].strip()
        result = "".join(decode_morse(char) for char in morse_str.split())
    else:
        return jsonify({"error": "Missing 'morse' or 'morse_chars'"}), 400
    
    return jsonify({"decoded": result})


@app.route("/api/encode", methods=["POST"])
def api_encode():
    """Encode text to Morse code.
    
    Request body:
        {
            "text": "HELLO"
        }
    """
    data = request.get_json()
    text = data.get("text", "")
    
    if not text:
        return jsonify({"error": "Missing 'text'"}), 400
    
    morse_code = encode_text(text)
    return jsonify({"morse_code": morse_code})


# ─────────────────────────────────────────────────────────────
# Calibration
# ─────────────────────────────────────────────────────────────

@app.route("/api/calibrate", methods=["POST"])
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
        
        # Train
        accuracy = tap_detector.train(bg_audio, tap_audio)
        
        return jsonify({
            "status": "trained",
            "accuracy": float(accuracy),
            "samples_bg": len(bg_audio),
            "samples_tap": len(tap_audio)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/calibrate-status", methods=["GET"])
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
            import base64
            data = request.get_json()
            audio_b64 = data.get("audio", "")
            if not audio_b64:
                return jsonify({"error": "Missing audio data"}), 400
            audio_bytes = base64.b64decode(audio_b64)
            audio_data = np.frombuffer(audio_bytes, dtype=np.float32)
        
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
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/process-signal", methods=["POST"])
def api_process_signal():
    """Process a complete signal (press duration) to classify as dot, dash, or reject.
    
    Request body (JSON):
        {
            "duration_ms": 250,        # Press duration in milliseconds
            "audio": [...],            # Optional: audio frame for ML validation
            "use_ml": true             # Whether to validate with ML model
        }
    """
    data = request.get_json()
    duration_ms = data.get("duration_ms", 0)
    use_ml = data.get("use_ml", tap_detector.is_trained)
    
    duration_s = duration_ms / 1000.0
    signal_type = classify_signal(duration_s)
    
    validation_result = {
        "valid": True,
        "reason": "No ML validation"
    }
    
    # Optional ML validation
    if use_ml and tap_detector.is_trained and "audio" in data:
        import base64
        try:
            audio_b64 = data["audio"]
            audio_bytes = base64.b64decode(audio_b64)
            audio_data = np.frombuffer(audio_bytes, dtype=np.float32)
            tap_prob, is_tap = tap_detector.predict(audio_data)
            validation_result["valid"] = is_tap
            validation_result["reason"] = f"ML validation: {tap_prob:.0%} confidence"
        except Exception as e:
            validation_result["valid"] = False
            validation_result["reason"] = f"ML validation failed: {str(e)}"
    
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
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
