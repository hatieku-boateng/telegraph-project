# Telegraph Backend API

Flask microservice for the Morse Code Telegraph Translator.

## Setup

```bash
cd backend
python3 -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
python app.py
```

Server runs on `http://localhost:5000`

## API Endpoints

### Health

**GET** `/api/health`

Check API status.

```json
{
  "status": "ok",
  "model_trained": false,
  "sample_rate": 44100
}
```

### Morse Decoding

**POST** `/api/decode`

Decode Morse code to text.

Request:
```json
{
  "morse_chars": ["...", "---", "..."]
}
```

Or:
```json
{
  "morse": "... --- ..."
}
```

Response:
```json
{
  "decoded": "SOS"
}
```

### Morse Encoding

**POST** `/api/encode`

Encode text to Morse code.

Request:
```json
{
  "text": "HELLO"
}
```

Response:
```json
{
  "morse_code": ".... . .-.. .-.. --- / ......"
}
```

### Calibration

**POST** `/api/calibrate`

Train the ML model (requires audio files).

Request (multipart/form-data):
- `background`: WAV file (5s silence)
- `taps`: WAV file (5s table taps)

Response:
```json
{
  "status": "trained",
  "accuracy": 0.94,
  "samples_bg": 1323,
  "samples_tap": 984
}
```

**GET** `/api/calibrate-status`

Check if model is trained.

Response:
```json
{
  "is_trained": true,
  "model_type": "RandomForest"
}
```

### Audio Processing

**POST** `/api/classify-tap`

Classify a single audio frame.

Request (JSON):
```json
{
  "audio": "base64_encoded_audio_data",
  "sample_rate": 44100
}
```

Or (multipart/form-data):
- `audio_file`: WAV file

Response:
```json
{
  "tap_probability": 0.85,
  "is_tap": true,
  "signal_type": "-",
  "duration_ms": 250,
  "model_trained": true
}
```

**POST** `/api/process-signal`

Process a press duration and classify as dot/dash.

Request:
```json
{
  "duration_ms": 150,
  "use_ml": true
}
```

Response:
```json
{
  "signal_type": ".",
  "duration_ms": 150,
  "validation": {
    "valid": true,
    "reason": "ML validation: 92% confidence"
  },
  "model_trained": true
}
```

### Settings

**GET** `/api/settings`

Get current signal processing configuration.

Response:
```json
{
  "dot_threshold_ms": 150,
  "letter_gap_ms": 400,
  "word_gap_ms": 1000,
  "gain": 100,
  "spike_factor": 3.0,
  "sample_rate": 44100
}
```

## Integration with Frontend

The React frontend communicates with these endpoints via CORS-enabled HTTP requests.

Example frontend hook usage:

```typescript
const response = await fetch('http://localhost:5000/api/decode', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ morse_chars: ['.-', '..', '...'] })
});
const data = await response.json();
console.log(data.decoded); // "AIS"
```

## Project Structure

```
backend/
  ├── app.py              # Flask API server
  ├── morse.py            # Morse encoding/decoding
  ├── signal_processor.py # Signal detection utilities
  ├── ml_model.py         # Tap detection ML model
  ├── requirements.txt    # Python dependencies
  └── README.md           # This file
```
