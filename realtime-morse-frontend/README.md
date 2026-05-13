

# ⚡ AI Morse Code Telegraph Translator - Frontend

A modern React/TypeScript web interface for the AI Morse Code Telegraph Translator. This frontend provides a real-time dashboard for Morse code input via keyboard, microphone, or text encoding, with live visualization and ML-powered signal detection.

**[🌐 Live Demo](#) | [📖 Full Docs](../INTEGRATION.md) | [🔧 Backend API](../backend/README.md) | [📚 Main Project](../README.md)**

---

## 🚀 Quick Start

### Prerequisites
- Node.js 16+
- npm or bun
- Backend API running (see [Backend Setup](../backend/README.md))

### Installation & Run

```bash
# Install dependencies
npm install  # or: bun install

# Start development server
npm run dev
```

Then open **http://localhost:8080** in your browser.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Usage Guide](#usage-guide)
- [Components](#components)
- [API Integration](#api-integration)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)

---

## Overview

This React frontend transforms your browser into a real-time Morse code translator with three input modes:

| Mode | How to Input | Use Case |
|------|-------------|----------|
| ⌨️ **Keyboard** | Hold Space bar | Fast, always available |
| 🎙️ **Microphone** | Tap the table | Immersive, hands-free |
| 📝 **Text Encoder** | Type text | Send pre-written messages |

The interface features:
- **Real-time visualization** of audio signals and Morse code
- **ML-powered tap detection** for microphone mode
- **Adaptive noise filtering** that adjusts to your environment
- **Message history** and Morse code reference
- **Text-to-speech output** for decoded messages

---

## Features

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

## Architecture

```
┌─────────────────────────────────────────┐
│        React Web Frontend               │
│   (Vite + TypeScript + Tailwind CSS)    │
├─────────────────────────────────────────┤
│  - TelegraphKey (Keyboard Input)        │
│  - AudioDecoder (Mic Processing)        │
│  - SignalVisualizer (Live Dashboard)    │
│  - TextToMorse (Text Encoding)          │
│  - MessageHistory (Session Storage)     │
└────────────────┬────────────────────────┘
                 │ HTTP/REST
                 ↓
┌─────────────────────────────────────────┐
│      Flask Backend API                  │
│   (Signal Processing, ML, Decoding)     │
└─────────────────────────────────────────┘
```

**Tech Stack:**
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS + shadcn/ui components
- **State Management**: React hooks + TanStack Query
- **Routing**: React Router
- **Testing**: Vitest + React Testing Library

---

## Project Structure

```
realtime-morse-frontend/
├── public/                       # Static assets
│   └── robots.txt
├── src/
│   ├── components/               # React components
│   │   ├── AudioDecoder.tsx      # Microphone input handler
│   │   ├── ControlsPanel.tsx     # Main control interface
│   │   ├── DecodedOutput.tsx     # Text output display
│   │   ├── MessageHistory.tsx    # Message history panel
│   │   ├── MorseReference.tsx    # Morse code lookup
│   │   ├── SignalVisualizer.tsx  # Live signal dashboard
│   │   ├── TelegraphKey.tsx      # Keyboard input component
│   │   ├── TextToMorse.tsx       # Text encoding interface
│   │   └── ui/                   # shadcn/ui components
│   ├── hooks/                    # Custom React hooks
│   │   ├── use-mobile.tsx        # Mobile detection
│   │   ├── use-toast.ts          # Toast notifications
│   │   ├── useApiTelegraph.ts    # Backend API integration
│   │   ├── useAudioDecoder.ts    # Audio processing
│   │   └── useTelegraph.ts       # Telegraph state management
│   ├── lib/                      # Utilities
│   │   ├── api.ts                # API client functions
│   │   ├── morse.ts              # Morse code utilities
│   │   └── utils.ts              # General utilities
│   ├── pages/                    # Page components
│   │   ├── Index.tsx             # Main application page
│   │   └── NotFound.tsx          # 404 page
│   ├── test/                     # Test files
│   │   ├── example.test.ts       # Example test
│   │   └── setup.ts              # Test configuration
│   ├── App.css                  # Global styles
│   ├── App.tsx                  # Main app component
│   ├── index.css                # Tailwind CSS imports
│   ├── main.tsx                 # App entry point
│   └── vite-env.d.ts            # Vite type definitions
├── package.json                  # NPM dependencies & scripts
├── tsconfig.json                 # TypeScript configuration
├── vite.config.ts                # Vite build configuration
├── tailwind.config.ts            # Tailwind CSS config
├── postcss.config.js             # PostCSS configuration
├── eslint.config.js              # ESLint configuration
└── README.md                     # This file
```

---

## Setup & Installation

### Prerequisites
- **Node.js 16+**
- **npm** or **bun** package manager
- **Backend API** running on `http://localhost:5000`

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd telegraph-project/realtime-morse-frontend

# Install dependencies
npm install
# or
bun install
```

### Development Server

```bash
# Start development server
npm run dev
# or
bun run dev
```

The app will be available at `http://localhost:8080`.

### Build for Production

```bash
# Build optimized bundle
npm run build

# Preview production build
npm run preview
```

---

## Usage Guide

### Step 1: Start the Backend
First, ensure the Flask backend is running:

```bash
cd ../backend
python app.py
```

### Step 2: Open the Frontend
Navigate to `http://localhost:8080` in your browser.

### Step 3: Choose Input Mode

#### Keyboard Mode
1. Click the **Keyboard** tab
2. Hold the **Space bar** to input Morse code
3. Short press (< 150ms) = dot (.)
4. Long press (≥ 150ms) = dash (-)
5. Watch the live visualization and decoded text

#### Microphone Mode
1. Click the **Microphone** tab
2. If prompted, calibrate by recording silence and taps
3. Tap the table to input Morse code
4. The ML model will filter real taps from noise

#### Text Encoder Mode
1. Click the **Text** tab
2. Type your message in the text box
3. Click **Encode** to see Morse code
4. Click **Play** to hear the Morse audio

### Step 4: View Results
- **Decoded Output**: Real-time text translation
- **Signal Visualizer**: Live audio levels and tap detection
- **Message History**: Previous messages (stored in browser)

---

## Components

### Core Components

| Component | Purpose |
|-----------|---------|
| `TelegraphKey` | Keyboard input with press duration detection |
| `AudioDecoder` | Microphone capture and ML tap classification |
| `SignalVisualizer` | Real-time audio visualization dashboard |
| `DecodedOutput` | Text output with TTS support |
| `TextToMorse` | Text-to-Morse encoding interface |
| `MessageHistory` | Session message storage and display |
| `MorseReference` | Interactive Morse code lookup table |

### UI Components (shadcn/ui)
- **Buttons, Inputs, Cards**: Standard form controls
- **Tabs**: Mode switching interface
- **Progress Bars**: Volume and signal visualization
- **Dialogs**: Calibration and settings modals
- **Toast**: User notifications

---

## API Integration

The frontend communicates with the Flask backend via REST API calls. All API functions are centralized in `src/lib/api.ts`.

### Key API Functions

```typescript
// Check if ML model is trained
const status = await checkCalibrationStatus();

// Decode Morse code to text
const decoded = await decodeMorse(['.-', '..', '...']); // "AIS"

// Encode text to Morse
const morse = await encodeText('HELLO'); // ".... . .-.. .-.. ---"

// Classify audio tap
const result = await classifyTap(audioBlob);

// Process signal duration
const signal = await processSignal(250); // 250ms press → "."
```

### Custom Hook: `useApiTelegraph`

```typescript
import { useApiTelegraph } from '@/hooks/useApiTelegraph';

function MyComponent() {
  const api = useApiTelegraph({ useBackend: true });
  
  // All API functions available
  const decoded = await api.decodeMorse(['.-']);
}
```

---

## Development

### Available Scripts

```bash
# Development server
npm run dev

# Build for production
npm run build

# Run linter
npm run lint

# Run tests
npm run test

# Run tests in watch mode
npm run test:watch
```

### Code Style
- **TypeScript**: Strict type checking enabled
- **ESLint**: React and TypeScript rules
- **Prettier**: Code formatting (via ESLint)

### Adding New Components

1. Create component in `src/components/`
2. Export from `src/components/index.ts` (if needed)
3. Add to appropriate page or layout

### Environment Variables

Create `.env.local` for local development:

```env
VITE_API_BASE_URL=http://localhost:5000
VITE_DEBUG=true
```

---

## Testing

Tests are written with Vitest and React Testing Library.

```bash
# Run all tests
npm run test

# Run tests in watch mode
npm run test:watch

# Run with coverage
npm run test:run -- --coverage
```

### Test Structure
- **Unit Tests**: Component logic and utilities
- **Integration Tests**: API calls and hooks
- **E2E Tests**: Full user workflows (planned)

---

## Deployment

### Docker Deployment

```bash
# Build Docker image
docker build -t telegraph-frontend .

# Run container
docker run -d -p 8080:8080 telegraph-frontend
```

### Static Hosting

The app builds to static files that can be hosted on any static host:

```bash
npm run build
# Upload dist/ folder to hosting service
```

### Environment Configuration

For production, set the API base URL:

```env
VITE_API_BASE_URL=https://your-backend-api.com
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **Backend connection failed** | Ensure backend is running on port 5000 |
| **Microphone not working** | Check browser permissions and HTTPS requirement |
| **Calibration stuck** | Refresh page and try again; check backend logs |
| **Build errors** | Clear node_modules and reinstall: `rm -rf node_modules && npm install` |
| **TypeScript errors** | Run `npm run lint` to see detailed errors |

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

---

## License

This project is provided as-is for educational purposes.
