# Integration Guide: Frontend + Backend

This document explains how the React frontend integrates with the Flask backend API.

## Architecture

```
┌──────────────────────────────┐
│   React Frontend             │
│   (Vite + TypeScript)        │
├──────────────────────────────┤
│  - TelegraphKey              │
│  - SignalVisualizer          │
│  - AudioDecoder              │
│  - TextToMorse               │
│  - Calibration UI            │
└──────────┬───────────────────┘
           │ HTTP/REST
           ↓
┌──────────────────────────────┐
│   Flask Backend API          │
│   (Python)                   │
├──────────────────────────────┤
│  - Morse encoding/decoding   │
│  - Signal classification     │
│  - ML model training         │
│  - Audio processing          │
└──────────────────────────────┘
```

## Frontend API Layer

The frontend communicates with the backend via `src/lib/api.ts`, which exports typed functions for all API endpoints.

### Key Hook: `useApiTelegraph`

```typescript
import { useApiTelegraph } from '@/hooks/useApiTelegraph';

function MyComponent() {
  const api = useApiTelegraph({ useBackend: true });
  
  // Check if ML model is trained
  if (!api.modelTrained) {
    return <CalibrationUI />;
  }
  
  // Classify a signal (dot/dash/invalid)
  const result = await api.classifySignalDuration(250); // 250ms press
  console.log(result.signal); // '.' or '-'
}
```

### Example: Using the Decode API

```typescript
import { decodeMorse } from '@/lib/api';

async function decodeTaps() {
  try {
    const text = await decodeMorse(['.-', '..', '...']); // A I S
    console.log(text); // "AIS"
  } catch (error) {
    console.error('Decode failed:', error);
  }
}
```

### Example: Audio Processing

```typescript
import { classifyTap } from '@/lib/api';

async function analyzeAudioFrame(audioBlob: Blob) {
  const result = await classifyTap(audioBlob);
  console.log(`Tap probability: ${(result.tap_probability * 100).toFixed(0)}%`);
  console.log(`Is tap: ${result.is_tap}`);
  console.log(`Signal type: ${result.signal_type}`); // '.' or '-'
}
```

## Backend Endpoints

All endpoints are prefixed with `/api` and hosted at `http://localhost:5000`.

### Core Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Check API status |
| POST | `/decode` | Decode Morse to text |
| POST | `/encode` | Encode text to Morse |
| POST | `/calibrate` | Train ML model |
| GET | `/calibrate-status` | Check if model trained |
| POST | `/classify-tap` | Classify audio frame |
| POST | `/process-signal` | Process press duration |
| GET | `/settings` | Get configuration |

See [backend/README.md](../backend/README.md) for detailed API documentation.

## Setup Instructions

### 1. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Ensure you have Python 3.8+ installed.

### 2. Start Backend Server

```bash
cd backend
python app.py
```

Server will run on `http://localhost:5000`.

### 3. Configure Frontend Environment

Create or update `.env` in the frontend directory:

```env
VITE_API_URL=http://localhost:5000/api
```

### 4. Install Frontend Dependencies

```bash
cd realtime-morse-frontend
npm install
```

### 5. Start Frontend Dev Server

```bash
npm run dev
```

Frontend will run on `http://localhost:8080`.

### 6. Access the Application

Open http://localhost:8080 in your browser.

## Feature Integration Status

✅ = Frontend component ready
🔄 = API integration in progress

| Feature | Frontend | Backend | Status |
|---------|----------|---------|--------|
| Keyboard Mode | ✅ TelegraphKey | ✅ morse.py | 🟢 Ready |
| Signal Visualization | ✅ SignalVisualizer | ✅ signal_processor.py | 🟢 Ready |
| Morse Decoding | ✅ DecodedOutput | ✅ /api/decode | 🟢 Ready |
| Text to Morse | ✅ TextToMorse | ✅ /api/encode | 🟢 Ready |
| Microphone Input | ✅ AudioDecoder | 🔄 /api/classify-tap | 🟡 Partial |
| ML Calibration | 🔄 CalibrationUI | ✅ /api/calibrate | 🟡 Partial |
| Message History | ✅ MessageHistory | ✅ Stored in frontend | 🟢 Ready |
| Morse Reference | ✅ MorseReference | ✅ morse.py dict | 🟢 Ready |

## Troubleshooting

### "Cannot find module" in frontend

```bash
# Regenerate API type definitions
npm run build

# Or, ensure .env.development is set
echo "VITE_API_URL=http://localhost:5000/api" > .env
```

### Backend not responding

- Check if `python app.py` is running in `backend/` folder
- Ensure `Flask` and `flask-cors` are installed: `pip install -r backend/requirements.txt`
- Check that port 5000 is not blocked by firewall

### CORS errors in browser

- Backend must have `flask-cors` installed
- Frontend must have correct `VITE_API_URL` in `.env`

### Model not trained

Before using ML features (microphone mode with advanced filtering):

1. Navigate to Calibration UI
2. Record 5 seconds of background noise
3. Record 5 seconds of table taps
4. Click "Train Model"
5. Wait for accuracy feedback

## Next Steps

- [ ] Add WebSocket support for real-time streaming audio
- [ ] Implement Calibration UI component
- [ ] Add error boundary and retry logic
- [ ] Create Docker compose file for development
- [ ] Add database for message history persistence
- [ ] Implement user authentication
