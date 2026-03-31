# Real-Time Morse Code Telegraph Decoder



**Real-Time Morse Code Telegraph Decoder**

This project implements a real-time Morse code decoding system that converts physical table taps captured through a laptop microphone into readable text. Built entirely in a Jupyter Notebook, it combines digital signal processing with machine learning to create a modern take on the classic telegraph.

The system listens to audio input in real time, applies software gain amplification, and uses a dual-gate detection pipeline: an adaptive noise floor threshold identifies potential tap events, while a trained Random Forest classifier validates each detected sound against 6 audio features (RMS energy, peak amplitude, crest factor, zero-crossing rate, spectral centroid, and attack sharpness) to filter out false positives from ambient noise.

Taps are classified as Morse dots or dashes based on duration, then grouped into letters and words using configurable silence gap timing. A live HTML dashboard updates 10 times per second, displaying a volume meter, ML classification status, the raw signal log, and the decoded text output.

The project features a one-time calibration step where users record 5 seconds of background noise and 5 seconds of tapping to train the classifier, which is then saved to disk for reuse across sessions. All detection parameters — gain, sensitivity, timing thresholds — are fully configurable to adapt to different environments and tapping styles.

**Technologies used:** Python, NumPy, sounddevice, scikit-learn (Random Forest), IPython/Jupyter, threading for concurrent audio processing and UI updates.

---

## Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage Guide](#usage-guide)
  - [Step 1: Run Setup Cells](#step-1-run-setup-cells)
  - [Step 2: Calibrate the Tap Detector (First Time Only)](#step-2-calibrate-the-tap-detector-first-time-only)
  - [Step 3: Start the Listener](#step-3-start-the-listener)
  - [Step 4: Tap Morse Code](#step-4-tap-morse-code)
- [Configurable Parameters](#configurable-parameters)
- [Morse Code Reference](#morse-code-reference)
- [Troubleshooting](#troubleshooting)
- [Architecture](#architecture)

---

## Overview

This project turns your laptop microphone into a Morse code receiver. Instead of using a traditional telegraph key, you simply **tap on your desk or table**. The system:

1. Captures audio in real time via `sounddevice`
2. Applies software gain amplification to detect subtle taps
3. Uses an **adaptive noise floor** to ignore ambient background sounds
4. Validates each detected tap with a **Random Forest ML classifier** trained on your specific environment
5. Classifies taps as dots (`.`) or dashes (`-`) based on duration
6. Groups symbols into letters using silence gap timing
7. Decodes Morse sequences into text using a built-in dictionary
8. Displays everything in a **live HTML dashboard** that updates 10 times per second

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

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd telegraph-project
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   # Using conda
   conda create -n telegraph python=3.10
   conda activate telegraph

   # Or using venv
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # macOS/Linux
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Open the notebook**:
   ```bash
   jupyter notebook build.ipynb
   ```
   Or open `build.ipynb` in VS Code with the Jupyter extension.

---

## Project Structure

```
telegraph-project/
├── build.ipynb          # Main notebook — all code lives here
├── tap_model.pkl        # Pre-trained Random Forest model (generated after calibration)
├── requirements.txt     # Python dependencies
├── README.md            # This file
└── .gitignore           # Git ignore rules
```

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
