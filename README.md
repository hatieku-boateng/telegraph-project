# ⚡ AI Morse Code Telegraph Translator

A real-time telegraph system combining **dual input modes** (keyboard & microphone), **ML-powered signal detection**, and a **modern web UI**. Transform table taps or button presses into Morse code and decode them to text instantly.

**[🌐 Live Demo](#) | [📖 Full Docs](./INTEGRATION.md) | [🔧 Backend API](./backend/README.md)**

---

## 🚀 Quick Start

### All-in-One (Simple)

If you just want to use the Jupyter notebook:
```bash
pip install -r requirements.txt
jupyter notebook build.ipynb
```

### Full Stack (Web UI + API)

```bash
# Terminal 1: Start the backend
cd backend && python app.py

# Terminal 2: Start the frontend
cd realtime-morse-frontend && npm run dev
```

Then open http://localhost:8080 in your browser.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features--modes)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage Guide](#usage-guide)
- [Troubleshooting](#troubleshooting)
- [API Documentation](#api-documentation)

---

## Overview

This project turns your laptop into a real-time Morse code translator. Choose your input mode:

| Mode | How to Input | Use Case |
|------|-------------|----------|
| ⌨️ **Keyboard** | Hold Space bar | Fast, always available |
| 🎙️ **Microphone** | Tap the table | Immersive, hands-free |
| 📝 **Text Encoder** | Type text | Send pre-written messages |

The system uses **adaptive thresholding** and an **ML classifier** (Random Forest) to distinguish real signals from noise, achieving high accuracy even in noisy environments.

---

## Architecture

```
┌─────────────────────────────────────────┐
│        React Web Frontend               │
│   (Keyboard, Mic Input, Text Encoder)   │
└────────────────┬────────────────────────┘
                 │ HTTP/REST
                 ↓
┌─────────────────────────────────────────┐
│      Flask Backend API                  │
│   (Signal Processing, ML, Decoding)     │
└────────────────┬────────────────────────┘
                 │
          ┌──────┴──────┐
          ↓             ↓
   ┌─────────────┐  ┌──────────────┐
   │  Python     │  │   Jupyter    │
   │  Modules    │  │  Notebook    │
   └─────────────┘  └──────────────┘
```

**Jupyter Notebook**: Traditional single-user interactive environment
**Web Stack**: React frontend + Flask backend for multi-user/remote access

---

## Features & Modes

### ⌨️ Keyboard Mode
- **Input**: Hold Space bar (short press = dot, long press = dash)
- **Auto-detection**: Automatic letter/word gap detection
- **Speed**: Adjustable timing thresholds
- **Feedback**: Live signal visualization + text-to-speech

### 🎙️ Microphone Mode
- **ML-Powered**: Random Forest classifier filters real taps from noise
- **Adaptive**: Auto-calibrates noise floor to your environment  
- **Training**: One-time 10-second calibration (record silence + taps)
- **Advanced**: 6 audio features for precise tap detection

### 📝 Text Encoder
- **Encode Text → Morse**: Convert any text to Morse code
- **Playable**: Optional audio output of Morse signals
- **Copy-ready**: One-click copy of Morse sequences

### 🧠 Advanced Features
- **TTS Output**: Decoded letters spoken aloud (macOS/Linux/Windows)
- **Message History**: Save and recall decoded messages
- **Morse Reference**: Built-in lookup dictionary
- **Real-time Visualization**: Volume meter, signal bars, live updates

---

## How It Works

```
Microphone → Software Gain → Adaptive Threshold Detection
                                      ↓
                              Tap Buffer (accumulate frames)
                                      ↓
                              Tap Ends → ML Validation (Random Forest)
                                      ↓
                              Classify Duration (dot vs dash)
                                      ↓
                              Gap Monitor (letter/word boundaries)
                                      ↓
                              Morse Dictionary Lookup → Decoded Text
```

### Detection Pipeline (Dual-Gate)

1. **Adaptive Threshold Gate**: The system maintains a running noise floor using exponential smoothing. A sound must exceed `noise_floor × SPIKE_FACTOR` to be considered a potential tap.

2. **ML Validation Gate**: When a tap ends, the loudest 1024-sample chunk is extracted and classified by a pre-trained Random Forest model using 6 audio features:
   - **RMS** (root mean square energy)
   - **Peak amplitude**
   - **Crest factor** (peak / RMS — high for sharp taps)
   - **Zero-crossing rate** (frequency content indicator)
   - **Spectral centroid** (brightness of sound)
   - **Attack sharpness** (first-quarter energy ratio)

3. Only sounds that pass **both** gates are recorded as Morse symbols.

---

## Features

- **Real-time live dashboard** with volume meter, ML status, signal log, and decoded text
- **Adaptive noise floor** — automatically adjusts to your environment
- **ML-powered tap filtering** — distinguishes real taps from accidental sounds
- **Persistent model** — train once, save to disk, reuse across sessions
- **ESC key to stop** — cleanly exits the listener at any time
- **Configurable parameters** — tune sensitivity, timing, and gain to your setup
- **Full Morse code support** — letters A-Z, numbers 0-9, and common punctuation

---

## Requirements

- **Python 3.8+**
- **Microphone** (built-in laptop mic works fine)
- **Jupyter Notebook** (VS Code Jupyter extension recommended)

### Python Packages

```
numpy
sounddevice
scikit-learn
keyboard
ipython
jupyter
```

> **Note**: The `keyboard` package requires **administrator/root privileges** on some systems to detect key presses globally.

---

## Installation

### Option 1: Jupyter Notebook (Simple)

```bash
# 1. Clone & navigate
git clone <your-repo-url>
cd telegraph-project

# 2. Create Python environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or: venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Open notebook
jupyter notebook build.ipynb
```

### Option 2: Full Stack (Web UI + Backend)

**Prerequisites:**
- Python 3.8+
- Node.js 16+
- npm or bun

```bash
# Clone repository
git clone <your-repo-url>
cd telegraph-project

# --- Backend Setup ---
cd backend
python -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# --- Frontend Setup (new terminal) ---
cd realtime-morse-frontend
npm install  # or: bun install

# --- Run in two terminals ---
# Terminal 1: Start backend
cd backend && python app.py

# Terminal 2: Start frontend
cd realtime-morse-frontend && npm run dev
```

Then open **http://localhost:8080** in your browser.

---

## Project Structure

```
telegraph-project/
├── build.ipynb                    # Jupyter notebook — keyboard + mic modes
├── backend/                       # Flask API backend
│   ├── app.py                     # Main Flask application
│   ├── morse.py                   # Morse encoding/decoding
│   ├── signal_processor.py        # Signal detection & features
│   ├── ml_model.py                # ML tap detector
│   ├── requirements.txt           # Python deps
│   └── README.md                  # Backend API docs
│
├── realtime-morse-frontend/       # React web frontend
│   ├── src/
│   │   ├── components/            # React components
│   │   ├── hooks/                 # Custom React hooks
│   │   ├── lib/                   # Utilities (API client, morse dict)
│   │   └── pages/                 # Pages
│   ├── package.json               # NPM dependencies
│   └── README.md                  # Frontend setup
│
├── tap_model.pkl                  # Pre-trained Random Forest (generated)
├── requirements.txt               # Jupyter notebook deps
├── README.md                      # This file
├── INTEGRATION.md                 # Frontend-Backend integration guide
└── .gitignore                     # Git ignore

---

## Usage Guide

### Step 1: Run Setup Cells

Run the following cells in order (cells 1–8 in the notebook):

| Cell | Purpose |
|------|---------|
| **Cell 2** | Import libraries (`sounddevice`, `numpy`, `sklearn`, etc.) |
| **Cell 4** | Define the Morse code dictionary (A-Z, 0-9, punctuation) |
| **Cell 6** | Set configurable parameters (GAIN, thresholds, timing) |
| **Cell 8** | Define helper functions (`classify_signal`, `decode_morse`, `extract_features`, etc.) |

### Step 2: Calibrate the Tap Detector (First Time Only)

> **Skip this step if `tap_model.pkl` already exists** — the listener will load it automatically.

To train a new model, **uncomment Cell 10** and run it. The calibration process:

1. **Records 5 seconds of silence** — sit still, don't touch anything
2. **Records 5 seconds of tapping** — tap the table repeatedly with consistent force
3. **Trains a Random Forest classifier** on the audio features
4. **Saves the model** to `tap_model.pkl`

You'll see output like:
```
🔇  Recording 5 seconds of BACKGROUND NOISE — do NOT tap...
   ✅ Background recorded.

🔊  Recording 5 seconds of TAPS — tap the table repeatedly NOW!
   ✅ Taps recorded.

   Training samples: 430 (390 noise, 40 tap)
   Training accuracy: 99.8%
   💾 Model saved to tap_model.pkl

✅  Tap detector model ready!
```

**Tips for good calibration:**
- Keep your environment quiet during the silence recording
- Tap consistently during the tap recording — use the same force you'll use for actual Morse code
- If accuracy is low, try increasing `GAIN` and re-running

### Step 3: Start the Listener

Run **Cell 12** (the Real-Time Morse Code Listener). You'll see a live dashboard:

```
✅ Loaded tap model from tap_model.pkl

🎤 Mic: |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░| ⚫ quiet  vol=0.0012  thresh=0.0036  floor=0.0012
Signals: no taps yet

Decoded: waiting for taps...
```

The dashboard updates in real time showing:
- **Volume bar** — shows current mic level and whether a tap was detected
- **Status indicators**:
  - 🟢 **TAP (95%)** — tap detected and accepted by ML
  - 🟡 **rejected (5%)** — spike detected but ML says it's not a tap
  - 🔵 **detecting...** — sound is currently active
  - ⚫ **quiet** — no sound above threshold
- **Signals** — raw dot/dash sequence with decoded letters
- **Decoded** — the final decoded text

### Step 4: Tap Morse Code

Use the **International Morse Code** timing:

| Action | Meaning |
|--------|---------|
| **Short tap** (< 0.15 seconds) | Dot (`.`) |
| **Long tap** (≥ 0.15 seconds) | Dash (`-`) |
| **Pause ~0.4 seconds** | End of letter |
| **Pause ~1.0 seconds** | Space between words |

**Example — tapping "HI":**
1. Tap quickly 4 times: `....` → **H**
2. Wait 0.4 seconds
3. Tap quickly 2 times: `..` → **I**

**To stop**: Press the **ESC** key.

---

## Configurable Parameters

Edit **Cell 6** to tune the system for your environment:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `GAIN` | `100` | Software amplification of raw mic input. Increase if taps aren't detected. |
| `SPIKE_FACTOR` | `3.0` | How many times louder than ambient noise a sound must be to trigger detection. Lower = more sensitive. |
| `NOISE_SMOOTH` | `0.997` | Noise floor smoothing factor (0–1). Higher = more stable floor, slower adaptation. |
| `DOT_DURATION` | `0.15` | Maximum duration (seconds) for a dot. Longer sounds become dashes. |
| `LETTER_GAP` | `0.40` | Silence duration (seconds) to finalize a letter. |
| `WORD_GAP` | `1.00` | Silence duration (seconds) to insert a space between words. |
| `SAMPLE_RATE` | `44100` | Audio sample rate in Hz. Usually no need to change. |

### Tuning Tips

- **Taps not detected?** → Lower `SPIKE_FACTOR` (try `2.0`) or increase `GAIN`
- **Too many false detections?** → Raise `SPIKE_FACTOR` or retrain the ML model
- **Letters merging?** → Increase `LETTER_GAP`
- **Words not separating?** → Increase `WORD_GAP`
- **Dots registering as dashes?** → Increase `DOT_DURATION` (try `0.20`)

---

## Morse Code Reference

### Letters
| Letter | Code | Letter | Code | Letter | Code |
|--------|------|--------|------|--------|------|
| A | `.-` | J | `.---` | S | `...` |
| B | `-...` | K | `-.-` | T | `-` |
| C | `-.-.` | L | `.-..` | U | `..-` |
| D | `-..` | M | `--` | V | `...-` |
| E | `.` | N | `-.` | W | `.--` |
| F | `..-.` | O | `---` | X | `-..-` |
| G | `--.` | P | `.--.` | Y | `-.--` |
| H | `....` | Q | `--.-` | Z | `--..` |
| I | `..` | R | `.-.` | | |

### Numbers
| Number | Code | Number | Code |
|--------|------|--------|------|
| 0 | `-----` | 5 | `.....` |
| 1 | `.----` | 6 | `-....` |
| 2 | `..---` | 7 | `--...` |
| 3 | `...--` | 8 | `---..` |
| 4 | `....-` | 9 | `----.` |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **No sound detected at all** | Check your mic is working. Run the Mic Diagnostic cell (uncomment Cell 14). Increase `GAIN`. |
| **"rejected" on every tap** | The ML model doesn't recognize your taps. Uncomment Cell 10, retrain, and re-save the model. |
| **Background noise triggers taps** | Increase `SPIKE_FACTOR` to 5.0+. Retrain in a quieter environment. |
| **`keyboard` module error** | Install with `pip install keyboard`. On Linux, run Jupyter with `sudo`. |
| **`tap_model.pkl` not found** | You need to run calibration first. Uncomment Cell 10 and run it. |
| **ESC doesn't stop the listener** | The `keyboard` library may need admin privileges. Alternatively, interrupt the kernel. |
| **Everything is dashes, no dots** | Lower `DOT_DURATION` (try `0.10`) or tap more quickly. |
| **Letters decode as `?`** | The dot/dash sequence doesn't match any Morse code entry. Check your timing between dots and dashes. |

---

## Architecture

```
build.ipynb
│
├── Cell 2:  Imports (sounddevice, numpy, sklearn, keyboard, etc.)
├── Cell 4:  Morse dictionary (A-Z, 0-9, punctuation)
├── Cell 6:  Parameters (GAIN, SPIKE_FACTOR, timing thresholds)
├── Cell 8:  Helper functions (measure_duration, classify_signal, decode_morse, extract_features)
├── Cell 10: Calibration — trains & saves Random Forest model [commented out after first use]
├── Cell 12: Real-time listener — loads model, runs audio callback, live HTML dashboard
└── Cell 14: Mic diagnostic — records 5s and shows volume stats [commented out]
```

### Threading Model

The listener uses three concurrent components:

1. **Audio callback** (sounddevice thread) — processes each audio frame, detects spikes, buffers tap audio, runs ML validation
2. **Gap monitor thread** — polls silence duration to determine letter/word boundaries
3. **Main thread** — drains the output queue and updates the live HTML display

All shared state is protected by a `threading.Lock` to prevent race conditions.

---

## License

This project is provided as-is for educational purposes.
