# Real-Time Morse Code Telegraph Decoder

> A hands-on student project that turns your **spacebar into a telegraph key**, decoding Morse code into readable text in real time — all inside a Jupyter Notebook.

---

## What This Project Does

This project lets you tap Morse code on your keyboard's spacebar and watch it decode into English text live. A quick tap becomes a **dot** (`.`), holding the spacebar longer becomes a **dash** (`-`), and the system automatically figures out where letters and words begin and end based on how long you pause between taps.

Everything runs inside a single Jupyter Notebook (`build.ipynb`) and displays a live HTML dashboard that updates 20 times per second, showing exactly what the system is seeing — your key presses, the dots and dashes it records, and the decoded text.

The project also includes (commented-out) code for a **microphone-based mode** that detects physical table taps using audio processing and a machine learning classifier. This is an optional advanced feature you can explore later.

**Technologies used:** Python, NumPy, sounddevice, scikit-learn (Random Forest), IPython/Jupyter, `keyboard` library, threading for concurrent input processing and UI updates.

---

## Table of Contents

- [Overview — How It Works](#overview--how-it-works)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage Guide](#usage-guide)
  - [Step 1: Run the Setup Cells](#step-1-run-the-setup-cells)
  - [Step 2: Run the Telegraph Listener](#step-2-run-the-telegraph-listener)
  - [Step 3: Tap Morse Code](#step-3-tap-morse-code)
  - [Step 4: Stop the Listener](#step-4-stop-the-listener)
- [Understanding the Code — Cell by Cell](#understanding-the-code--cell-by-cell)
  - [Cell 1–2: Importing Libraries](#cell-12-importing-libraries)
  - [Cell 3–4: The Morse Code Dictionary](#cell-34-the-morse-code-dictionary)
  - [Cell 5–6: Configurable Parameters](#cell-56-configurable-parameters)
  - [Cell 7–8: Helper Functions](#cell-78-helper-functions)
  - [Cell 9–10: ML Calibration (Optional, Commented Out)](#cell-910-ml-calibration-optional-commented-out)
  - [Cell 11–12: The Keyboard Telegraph Listener](#cell-1112-the-keyboard-telegraph-listener)
  - [Cell 13–14: Mic Diagnostic (Optional, Commented Out)](#cell-1314-mic-diagnostic-optional-commented-out)
- [How Word Spacing Works](#how-word-spacing-works)
- [Configurable Parameters Reference](#configurable-parameters-reference)
- [Morse Code Reference](#morse-code-reference)
- [Troubleshooting](#troubleshooting)
- [Architecture & Threading Model](#architecture--threading-model)

---

## Overview — How It Works

The keyboard telegraph mode follows this pipeline:

```
Spacebar Press/Release → Measure Hold Duration → Classify as Dot or Dash
                                                          ↓
                                                 Append to Symbol Buffer
                                                          ↓
                                          Gap Monitor Thread (runs in background)
                                                 ↓                    ↓
                                        0.4s silence:           1.0s silence:
                                        decode letter           insert space
                                                 ↓                    ↓
                                          Morse Dictionary Lookup → Decoded Text
                                                          ↓
                                                 Live HTML Dashboard
```

**In plain English:**
1. You press the spacebar → the system starts a timer
2. You release the spacebar → the system measures how long you held it
3. If the hold was **short** (under 0.15 seconds) → it records a **dot** (`.`)
4. If the hold was **long** (0.15 seconds or more) → it records a **dash** (`-`)
5. Dots and dashes accumulate in a buffer (e.g., `....` for the letter H)
6. A background thread watches for pauses:
   - **0.4 seconds** of silence → the buffer is looked up in the Morse dictionary and decoded into a letter
   - **1.0 seconds** of silence → a space is inserted between words
7. The live dashboard updates continuously, showing everything in real time

---

## Features

- **Spacebar as telegraph key** — quick tap = dot, long press = dash
- **Automatic letter detection** — pausing 0.4 seconds finalizes a letter
- **Automatic word spacing** — pausing 1.0 seconds inserts a space between words
- **Live HTML dashboard** — visual hold-time bar, signal log, and decoded text, updating 20×/second
- **Visual dot/dash boundary** — an orange marker on the hold bar shows exactly where dot ends and dash begins
- **Full Morse code support** — all 26 letters (A–Z), digits (0–9), and 16 punctuation marks
- **ESC key to stop** — cleanly exits the listener and shows final decoded text
- **Fully configurable timing** — adjust dot duration, letter gap, and word gap to match your tapping speed
- **Optional ML microphone mode** — commented-out code for detecting physical table taps via audio (advanced)
- **Optional mic diagnostic** — commented-out tool to test your microphone's volume levels

---

## Requirements

- **Python 3.8+**
- **Jupyter Notebook** (VS Code with the Jupyter extension is recommended)
- **A keyboard** (the spacebar is used as the telegraph key)
- **Administrator privileges** may be required for the `keyboard` library on some systems

### Python Packages

```
numpy
sounddevice
scikit-learn
keyboard
ipython
jupyter
```

Install them all at once with:
```bash
pip install -r requirements.txt
```

> **Important:** The `keyboard` package hooks into low-level OS key events. On **Linux**, you must run Jupyter with `sudo`. On **Windows**, running as a normal user usually works. On **macOS**, you may need to grant accessibility permissions.

---

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/hatieku-boateng/telegraph-project.git
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
   Or open `build.ipynb` directly in VS Code with the Jupyter extension installed.

---

## Project Structure

```
telegraph-project/
├── build.ipynb          # Main notebook — all code lives here (14 cells)
├── tap_model.pkl        # Pre-trained Random Forest model (generated after calibration, optional)
├── requirements.txt     # Python dependencies
├── README.md            # This file
└── .gitignore           # Git ignore rules
```

---

## Usage Guide

### Step 1: Run the Setup Cells

Run these notebook cells **in order** before starting the telegraph:

| Cell # | Type     | What It Does |
|--------|----------|--------------|
| 1      | Markdown | Section header (just a label, nothing to run) |
| 2      | Python   | Imports all required libraries |
| 3      | Markdown | Section header |
| 4      | Python   | Defines the Morse code dictionary |
| 5      | Markdown | Section header |
| 6      | Python   | Sets configurable timing and audio parameters |
| 7      | Markdown | Section header |
| 8      | Python   | Defines helper functions used by the listener |

After running cells 2, 4, 6, and 8, all the building blocks are ready.

### Step 2: Run the Telegraph Listener

Run **Cell 12** (the large code cell under "Real-Time Morse Code Listener"). You'll immediately see:

```
Spacebar = telegraph key  |  ESC = stop

⌨️ Key: |░░░░░░░░░░░░░┃░░░░░░░░░░░░░░░░░░░░░░░░░░░| ⚫ ready
Signals: press spacebar to tap

Decoded: press spacebar to start...
```

The dashboard is live and waiting for your input.

### Step 3: Tap Morse Code

Use the **spacebar** as your telegraph key:

| What You Do | What the System Records |
|-------------|------------------------|
| **Quick tap** (< 0.15s) — tap and release immediately | Dot `.` |
| **Long press** (≥ 0.15s) — hold spacebar, then release | Dash `-` |
| **Wait 0.4 seconds** after releasing | Finalizes the current letter |
| **Wait 1.0 seconds** after releasing | Inserts a space (word boundary) |

**Example — typing "HI THERE":**

1. Tap spacebar quickly **4 times** → `....` (these become dots)
2. **Pause ~0.5 seconds** → system decodes `....` as **H**
3. Tap spacebar quickly **2 times** → `..`
4. **Wait 1 full second** → system decodes `..` as **I**, then inserts a **space**
5. **Hold spacebar** for ~0.2 seconds, release → `-` (dash = **T**)
6. Continue tapping the remaining letters...

**While you tap**, the dashboard updates in real time:
- The **hold bar** fills up as you hold the spacebar (green while pressed)
- The **orange line** (┃) marks the dot/dash boundary at 0.15 seconds
- **Signals** shows the raw dots, dashes and decoded letters: `.... [H] .. [I]   - [T] ...`
- **Decoded** shows the final text: `HI T...`

### Step 4: Stop the Listener

Press **ESC** at any time. The system will:
1. Stop the main loop
2. Decode any remaining symbols in the buffer
3. Display the final decoded text
4. Clean up the background thread

---

## Understanding the Code — Cell by Cell

This section walks through every cell in the notebook so you understand exactly what each piece does and why.

### Cell 1–2: Importing Libraries

**Cell 1** is a markdown header. **Cell 2** imports all the Python packages:

```python
import sounddevice as sd      # Audio recording from the microphone
import numpy as np             # Numerical operations (arrays, math)
import time                    # Measuring elapsed time for tap durations
import threading               # Running the gap monitor in the background
import queue                   # Thread-safe communication between threads
import keyboard                # Detecting spacebar and ESC key presses
from IPython.display import display, HTML   # Rendering live HTML in Jupyter
from sklearn.ensemble import RandomForestClassifier  # ML classifier (optional mic mode)
import pickle                  # Saving/loading the trained model to disk
```

**Why these libraries?**
- `keyboard` is the core input library — it detects when the spacebar is pressed and released at the OS level, so it works even when the notebook cell doesn't have focus
- `threading` and `queue` let us run the gap-monitoring logic simultaneously alongside the main input loop without blocking
- `IPython.display` with `display_id=True` allows us to update the same HTML output cell repeatedly, creating a live dashboard effect
- The audio/ML libraries (`sounddevice`, `numpy`, `sklearn`, `pickle`) are used by the optional microphone mode

### Cell 3–4: The Morse Code Dictionary

**Cell 4** defines the complete Morse code lookup table as a Python dictionary:

```python
morse_dict = {
    ".-": "A", "-...": "B", "-.-.": "C", ...
}
```

**How it works:**
- The **keys** are strings of dots and dashes (e.g., `".-"`)
- The **values** are the corresponding characters (e.g., `"A"`)
- When the system accumulates a sequence like `".-"`, it simply does `morse_dict.get(".-")` to get `"A"`
- If a dot/dash sequence doesn't match anything in the dictionary (e.g., you tapped `".-.-.-.-"`), the lookup returns `"?"` as a fallback

**What's included:**
- All 26 letters A–Z
- All 10 digits 0–9
- 16 punctuation marks: `. , ? ' ! / ( ) & : ; = + - _ " $ @`

### Cell 5–6: Configurable Parameters

**Cell 6** defines all the tunable constants in one place:

```python
DOT_DURATION    = 0.15    # Max seconds for a dot (longer = dash)
LETTER_GAP      = 0.40    # Silence seconds to finalise a letter
WORD_GAP        = 1.00    # Silence seconds to insert a space
```

**The three timing parameters (keyboard mode):**

| Parameter | Value | What It Controls |
|-----------|-------|------------------|
| `DOT_DURATION` | `0.15` seconds | The boundary between a dot and a dash. If you hold the spacebar for **less** than this, it's a dot. **More** than this → dash. |
| `LETTER_GAP` | `0.40` seconds | How long the system waits after your last release before it decides you're done with a letter and decodes the accumulated symbols. |
| `WORD_GAP` | `1.00` seconds | How long the system waits before inserting a space between words. Must be longer than `LETTER_GAP`. |

**The audio parameters** (`GAIN`, `SPIKE_FACTOR`, `NOISE_SMOOTH`, `MIN_TAP_VOLUME`, `COOLDOWN`, `SAMPLE_RATE`) are only used by the optional mic-based mode and the mic diagnostic. They have no effect on the keyboard telegraph.

### Cell 7–8: Helper Functions

**Cell 8** defines four helper functions. Here's what each one does:

#### `measure_duration(start_time)`
```python
def measure_duration(start_time):
    return time.time() - start_time
```
Returns how many seconds have passed since `start_time`. Used to measure how long the spacebar was held (though the main loop calculates this inline too).

#### `classify_signal(duration, dot_limit=DOT_DURATION)`
```python
def classify_signal(duration, dot_limit=DOT_DURATION):
    return "." if duration < dot_limit else "-"
```
Takes a duration in seconds and returns `"."` (dot) if it's shorter than `DOT_DURATION`, or `"-"` (dash) if it's longer. This is the core classification logic — just a simple threshold comparison.

#### `decode_morse(symbol_buffer, dictionary=None)`
```python
def decode_morse(symbol_buffer, dictionary=None):
    if dictionary is None:
        dictionary = morse_dict
    return dictionary.get(symbol_buffer, "?")
```
Takes a string of dots and dashes (e.g., `".-"`) and looks it up in the Morse dictionary. Returns the decoded character (e.g., `"A"`) or `"?"` if the sequence is not valid Morse code. The optional `dictionary` parameter lets you pass a different lookup table if needed.

#### `extract_features(block)`
```python
def extract_features(block):
    ...
    return np.array([rms, peak, crest_factor, zcr, spectral_centroid, attack])
```
This is only used by the **optional mic mode**. It takes a chunk of audio samples and computes 6 numerical features that describe the sound:

| Feature | What It Measures | Why It Matters |
|---------|------------------|----------------|
| `rms` | Root mean square energy — overall loudness | Taps are louder than background noise |
| `peak` | Maximum amplitude in the chunk | Taps have sharp peaks |
| `crest_factor` | `peak / rms` — how "spiky" the sound is | Taps have high crest (sharp transient), ambient noise doesn't |
| `zcr` | Zero-crossing rate — how often the signal crosses zero | Helps distinguish taps from hums or tones |
| `spectral_centroid` | "Center of mass" of the frequency spectrum | Taps tend to have broad, high-frequency content |
| `attack` | Energy in the first quarter vs total energy | Taps front-load their energy (loud start, quick decay) |

These 6 features are fed into the Random Forest classifier to decide "is this a real tap or just noise?"

### Cell 9–10: ML Calibration (Optional, Commented Out)

**Cell 10** is entirely commented out. If you uncomment and run it, it performs a calibration sequence for the microphone-based tap detection:

1. **Records 5 seconds of silence** — the system captures your room's background noise
2. **Records 5 seconds of tapping** — you tap the table/desk repeatedly
3. **Extracts features** from both recordings using `extract_features()` on 1024-sample blocks
4. **Labels the data** — background blocks get label `0`, tap blocks (that are louder than 2× the background RMS) get label `1`
5. **Trains a Random Forest** with 50 decision trees, max depth 8
6. **Saves the model** to `tap_model.pkl` using `pickle`

The model is saved with an MD5 hash check to avoid overwriting an identical model.

> **You don't need this for keyboard mode.** Only uncomment it if you want to experiment with the mic-based tap detection.

### Cell 11–12: The Keyboard Telegraph Listener

This is the main cell — the heart of the project. It has four major sections:

#### 1. Shared State Variables

```python
key_down        = False           # Is the spacebar currently being held?
start_time      = 0.0             # When was the spacebar pressed?
last_release    = 0.0             # When was it last released?
symbol_buffer   = ""              # Current dot/dash sequence (e.g., "..-")
decoded_text    = ""              # All decoded text so far
gap_checked     = False           # Has the current silence gap been processed?
word_gap_inserted = False         # Has a word space been inserted for this gap?
```

These variables are shared between the main loop thread and the gap-monitoring thread. They are protected by a `threading.Lock` — every read or write happens inside a `with lock:` block to prevent race conditions (two threads trying to modify the same variable at the same time).

#### 2. Gap Monitoring Thread (`group_symbols()`)

```python
def group_symbols():
    global symbol_buffer, decoded_text, gap_checked, word_gap_inserted
    while not stop_event.is_set():
        time.sleep(0.05)
        with lock:
            if key_down or last_release == 0.0:
                continue
            silence = time.time() - last_release

            if silence >= LETTER_GAP and symbol_buffer and not gap_checked:
                letter = decode_morse(symbol_buffer)
                decoded_text += letter
                output_q.put(("letter", letter))
                symbol_buffer = ""
                gap_checked = True
                word_gap_inserted = False

            if silence >= WORD_GAP and gap_checked and not word_gap_inserted:
                decoded_text += " "
                output_q.put(("space", " "))
                word_gap_inserted = True
```

**What this does:** Runs in a separate thread, checking every 50ms whether enough silence has passed to finalize a letter or insert a word space.

**Why two separate checks?**
- The letter gap (0.4s) always occurs **before** the word gap (1.0s)
- When the letter gap fires, the `symbol_buffer` is decoded and cleared, and `gap_checked` is set to `True`
- When the word gap fires (0.6 seconds later), the buffer is already empty — so instead of checking `symbol_buffer`, it checks `gap_checked` (meaning "a letter was just decoded") and inserts a space
- `word_gap_inserted` prevents the space from being inserted repeatedly on every 50ms poll cycle

**Why a separate thread?** The main loop is busy polling the keyboard. If we checked gaps in the main loop, we'd need extra logic to handle the timing. A dedicated thread makes the gap detection cleaner and more reliable.

#### 3. HTML Dashboard (`render_html()`)

This function generates a fresh HTML string every time it's called and returns an `IPython.display.HTML` object. Key elements:

- **Hold-time bar**: A 40-character visual bar that fills up as you hold the spacebar
  - Green (`#4caf50`) while the key is held
  - Blue (`#2196f3`) after a dot or dash is recorded
  - Grey (`#666`) when idle
- **Orange dot/dash boundary marker** (`┃`): A vertical line at the position corresponding to `DOT_DURATION` — if the bar fills past this line, you're in dash territory
- **State indicator**: Shows 🟢 KEY DOWN, ⚪ dot recorded, 🔵 dash recorded, or ⚫ ready
- **Signals line**: The raw log of dots, dashes, and decoded letters
- **Decoded line**: The final decoded text in large green font

The bar scaling uses a `cap` value of `DOT_DURATION × 3` (0.45s by default) as the maximum. This means the bar shows the most useful range for distinguishing dots from dashes.

#### 4. Main Loop

```python
try:
    while True:
        if keyboard.is_pressed('esc'):
            break
        space_pressed = keyboard.is_pressed('space')
        with lock:
            if space_pressed and not key_down:
                # Key just pressed — start timing
                ...
            elif not space_pressed and key_down:
                # Key just released — classify and record
                ...
        # Drain the output queue and update the dashboard
        ...
        time.sleep(0.05)
finally:
    # Clean up: stop gap thread, decode remaining buffer, show final output
    ...
```

**The main loop runs every 50ms (20 times per second) and does three things:**

1. **Polls the keyboard** — checks if spacebar is pressed or ESC is pressed
2. **Detects key transitions**:
   - **Press detected** (`space_pressed and not key_down`): records the press time, resets gap flags
   - **Release detected** (`not space_pressed and key_down`): calculates the hold duration, calls `classify_signal()` to determine dot vs dash, appends to `symbol_buffer`, puts the symbol on the output queue
3. **Updates the display** — drains any pending items from the output queue (symbols, decoded letters, spaces) and updates the live HTML dashboard

**The `finally` block** ensures clean shutdown: it signals the gap thread to stop, waits for it to finish, decodes any remaining symbols in the buffer (so the last letter isn't lost), and updates the dashboard one final time with the complete output.

### Cell 13–14: Mic Diagnostic (Optional, Commented Out)

**Cell 14** is a diagnostic tool for the microphone mode. If you uncomment and run it:

1. Records 5 seconds of audio with the configured `GAIN`
2. Computes RMS volume for every 1024-sample block
3. Prints min/max/mean volume statistics
4. Shows whether taps are detectable above the ambient noise floor
5. Displays a visual timeline where `█` = loud (tap), `▄` = medium, `░` = quiet

This helps you tune `GAIN` and `SPIKE_FACTOR` before running the mic-based listener.

---

## How Word Spacing Works

This is a subtle but important detail. Here's exactly how the system inserts spaces between words:

1. You finish tapping a letter (e.g., `..` for I) and lift your finger
2. The gap monitor thread starts counting silence from `last_release`
3. At **0.4 seconds** of silence: the `LETTER_GAP` fires
   - `symbol_buffer` (`".."`) is decoded to `"I"`
   - `decoded_text` becomes `"HI"` (appended)
   - `symbol_buffer` is cleared to `""`
   - `gap_checked` is set to `True`
   - `word_gap_inserted` is set to `False`
4. You keep waiting...
5. At **1.0 seconds** of silence: the `WORD_GAP` fires
   - The check sees `gap_checked is True` (a letter was decoded) and `word_gap_inserted is False`
   - A space `" "` is appended to `decoded_text` → `"HI "`
   - `word_gap_inserted` is set to `True` (prevents duplicate spaces)
6. When you start tapping again, `gap_checked` resets to `False`

**Key insight:** The letter gap always fires before the word gap (0.4s < 1.0s), so by the time the word gap check runs, the symbol buffer is already empty. That's why the word gap check uses `gap_checked` (a flag) instead of `symbol_buffer` (which would be empty).

---

## Configurable Parameters Reference

Edit **Cell 6** to tune the system. The three **keyboard mode** parameters are the most important:

### Keyboard Mode Timing

| Parameter | Default | What It Does |
|-----------|---------|--------------|
| `DOT_DURATION` | `0.15` s | Maximum hold time for a dot. If you hold the spacebar for **less** than this, it's a dot; **more** → dash. |
| `LETTER_GAP` | `0.40` s | How long to wait after the last key release before decoding the accumulated symbols as a letter. |
| `WORD_GAP` | `1.00` s | How long to wait before inserting a space between words. Must be greater than `LETTER_GAP`. |

### Mic Mode Parameters (optional)

| Parameter | Default | What It Does |
|-----------|---------|--------------|
| `GAIN` | `100` | Software amplification of raw mic input. Higher = more sensitive to quiet taps. |
| `SPIKE_FACTOR` | `3.0` | A sound must be this many times louder than the noise floor to count as a potential tap. |
| `NOISE_SMOOTH` | `0.997` | Noise floor smoothing factor (0–1). Higher = more stable baseline, slower to adapt to changes. |
| `MIN_TAP_VOLUME` | `0.05` | Absolute minimum volume threshold. Below this, nothing is detected regardless of spike factor. |
| `COOLDOWN` | `0.05` s | Seconds to ignore new spikes after a tap ends. Prevents echo/reverb from triggering false taps. |
| `SAMPLE_RATE` | `44100` Hz | Audio sample rate. Standard CD quality. No need to change this. |

### Tuning Tips

- **Everything registers as a dash, never a dot** → You're tapping too slow. Try increasing `DOT_DURATION` to `0.20` or `0.25`
- **Everything registers as a dot, never a dash** → You're not holding long enough. Try decreasing `DOT_DURATION` to `0.10`
- **Letters merge together** (e.g., `....` should be H but you get `....` + `..` = `......` = ?) → Increase `LETTER_GAP` to `0.60`
- **Words don't have spaces** → Increase `WORD_GAP` or wait longer between words (count "one-Mississippi")
- **Letters decode too slowly** → Decrease `LETTER_GAP` to `0.30` (but don't go below `DOT_DURATION`)

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

### Punctuation
| Symbol | Code | Symbol | Code |
|--------|------|--------|------|
| `.` | `.-.-.-` | `:` | `---...` |
| `,` | `--..--` | `;` | `-.-.-.` |
| `?` | `..--..` | `=` | `-...-` |
| `'` | `.----.` | `+` | `.-.-.` |
| `!` | `-.-.--` | `-` | `-....-` |
| `/` | `-..-.` | `_` | `..--.-` |
| `(` | `-.--.` | `"` | `.-..-.` |
| `)` | `-.--.-` | `$` | `...-..-` |
| `&` | `.-...` | `@` | `.--.-.` |

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| **Nothing happens when I press spacebar** | `keyboard` library can't detect key presses | Run Jupyter/VS Code as **administrator**. On Linux, use `sudo`. |
| **All letters decode as `?`** | Your dot/dash sequence doesn't match any Morse entry | Check the Morse code reference above. Make sure you're pausing long enough between letters (0.4s). |
| **No spaces between words** | Not waiting long enough | Wait a full second (count "one-Mississippi") between words. |
| **Everything is dashes** | You're tapping too slowly | Tap faster, or increase `DOT_DURATION` to `0.20` or `0.25`. |
| **Everything is dots** | You're not holding long enough for dashes | Hold the spacebar for at least 0.2 seconds for a dash. |
| **ESC doesn't stop it** | `keyboard` needs admin privileges | Interrupt the kernel instead (the stop button in Jupyter/VS Code). |
| **`ModuleNotFoundError: keyboard`** | Package not installed | Run `pip install keyboard`. |
| **Dashboard doesn't update** | Jupyter display issue | Make sure you're running in a Jupyter environment (not a plain Python script). |
| **Letters keep merging** | Pauses between letters are too short | Increase `LETTER_GAP` to `0.50` or `0.60`, or slow down between letters. |

---

## Architecture & Threading Model

```
build.ipynb
│
├── Cell 2 .... Imports (sounddevice, numpy, sklearn, keyboard, IPython, etc.)
├── Cell 4 .... Morse dictionary ({dot/dash string → character})
├── Cell 6 .... Parameters (DOT_DURATION, LETTER_GAP, WORD_GAP, audio settings)
├── Cell 8 .... Helper functions (measure_duration, classify_signal, decode_morse, extract_features)
├── Cell 10 ... ML Calibration [commented out] — trains Random Forest on tap vs noise audio
├── Cell 12 ... Keyboard Telegraph Listener — main loop, gap monitor, live HTML dashboard
└── Cell 14 ... Mic Diagnostic [commented out] — records audio and shows volume statistics
```

### Threading Model

The keyboard telegraph listener uses **two concurrent threads**:

```
┌─────────────────────────────────────┐
│  MAIN THREAD                        │
│  (Cell 12 main loop)                │
│                                     │
│  • Polls keyboard every 50ms        │
│  • Detects spacebar press/release   │
│  • Measures hold duration           │
│  • Classifies dot vs dash           │
│  • Drains output queue              │
│  • Updates live HTML dashboard      │
└────────────────┬────────────────────┘
                 │ shared state (protected by threading.Lock)
                 │ - key_down, symbol_buffer, decoded_text
                 │ - last_release, gap_checked, word_gap_inserted
                 │
┌────────────────┴────────────────────┐
│  GAP MONITOR THREAD                 │
│  (group_symbols function)           │
│                                     │
│  • Runs in background (daemon)      │
│  • Checks silence duration          │
│  • Fires letter gap at 0.4s         │
│  • Fires word gap at 1.0s           │
│  • Puts decoded letters/spaces      │
│    onto the output queue            │
└─────────────────────────────────────┘
```

**Communication between threads:**
- **Shared globals** (`symbol_buffer`, `decoded_text`, etc.) are read/written inside `with lock:` blocks
- **Output queue** (`queue.Queue`) is thread-safe and carries `(kind, value)` tuples:
  - `("symbol", ".")` — a dot was recorded
  - `("symbol", "-")` — a dash was recorded
  - `("letter", "H")` — a letter was decoded
  - `("space", " ")` — a word space was inserted
- **Stop event** (`threading.Event`) signals the gap thread to exit cleanly when ESC is pressed

---

## License

This project is provided as-is for educational purposes.
