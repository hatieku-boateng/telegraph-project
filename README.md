# 📡 Telegraph Messenger

A full-stack Morse code telegraph messenger with:
- **Real-time keyboard + microphone Morse input**
- **ML-powered tap detection** and adaptive noise filtering
- **JWT-authenticated users** and persistent conversation history
- **React + Vite frontend** with live Socket.IO chat
- **Notebook demo** for audio processing and training

**Docs:** [Backend API](./backend/README.md) · [Frontend Guide](./realtime-morse-frontend/README.md) · [Integration](./INTEGRATION.md) · [Deployment](./DEPLOYMENT.md)

---

## 🚀 What’s Included

This repository includes:
- A **Flask backend** with authentication, messaging, and real-time Socket.IO support
- A **React/TypeScript frontend** for telegraph input, decoding, and chat
- **SQLite persistence** via SQLAlchemy
- **Adaptive ML audio signal processing** for microphone tap detection
- A **Jupyter notebook demo** showing the signal pipeline and model calibration

---

## Table of Contents

- [Overview](#overview)
- [Current Updates](#current-updates)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Environment Setup](#environment-setup)
- [Project Structure](#project-structure)
- [Run Locally](#run-locally)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Related Docs](#related-docs)

---

## Overview

Telegraph Messenger is a full-stack project for translating Morse code in real time and sharing decoded messages in a chat application.

Input modes include:
- **Keyboard** (hold Space for dots/dashes)
- **Microphone** (tap table/microphone input)
- **Text encoder** (type and convert to Morse)

The backend also supports user accounts, conversations, and Socket.IO-powered real-time messaging.

---

## Current Updates

This README now reflects the repository’s current state and updates:
- **Auth-enabled backend** with signup/login/logout/profile endpoints
- **Message and conversation API** routes for persistent chat
- **Socket.IO real-time messaging** and presence events
- **Frontend state management and hooks** for live app flows
- **Dedicated component docs** in `backend/README.md` and `realtime-morse-frontend/README.md`
- **Docker Compose support** for easy local setup

---

## Architecture

```
┌────────────────────────────────────────────┐
│              React Web Frontend             │
│   (keyboard, mic, text input, chat UI)      │
└──────────────────────┬──────────────────────┘
                       │ HTTP/REST + Socket.IO
                       ↓
┌────────────────────────────────────────────┐
│              Flask Backend API              │
│   (auth, conversations, messages, signal ML)│
└──────────────────────┬──────────────────────┘
                       │
          ┌────────────┴────────────┐
          ↓                         ↓
   ┌─────────────────┐       ┌────────────────────┐
   │  SQLite/SQLAlchemy │     │  Jupyter Notebook  │
   │  Persistence       │     │  Demo & ML Pipeline│
   └─────────────────┘       └────────────────────┘
```

The repository can run as:
- a **full-stack web app** for real-time telegraph chat
- a **Jupyter notebook demo** for audio ML and tap detection

---

## Quick Start

### Recommended: Docker Compose

```bash
docker-compose up --build
```

This starts:
- **Backend** on `http://localhost:5000`
- **Frontend** on `http://localhost:8080`

Press `Ctrl+C` to stop.

### Manual Local Setup

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py

# Frontend (new terminal)
cd realtime-morse-frontend
npm install
npm run dev
```

Open **http://localhost:8080**.

---

## Environment Setup

### Backend `.env`

Create `backend/.env` with:

```env
FLASK_ENV=development
DEBUG=True
API_PORT=5000
CORS_ORIGINS=http://localhost:8080
JWT_SECRET_KEY=your_jwt_secret
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///telegraph_messenger.db
```

### Frontend `.env`

Create `realtime-morse-frontend/.env` with:

```env
VITE_API_URL=http://localhost:5000/api
```

---

## Project Structure

```
telegraph-project/
├── backend/                       # Flask backend and Socket.IO service
│   ├── app.py                     # Backend entry point
│   ├── config.py                  # App configuration
│   ├── database/                  # SQLAlchemy setup
│   ├── models/                    # DB models (users, conversations, messages)
│   ├── routes/                    # Auth and messaging API blueprints
│   ├── sockets/                   # Socket.IO event handlers
│   ├── requirements.txt           # Python dependencies
│   └── README.md                  # Backend docs
├── realtime-morse-frontend/       # React + TypeScript UI
│   ├── public/                    # Static assets
│   ├── src/                       # Application source code
│   ├── package.json               # Node dependencies and scripts
│   └── README.md                  # Frontend docs
├── build.ipynb                    # Notebook demo and ML pipeline walkthrough
├── docker-compose.yml             # Local dev orchestration
├── requirements.txt               # Notebook dependencies
├── README.md                      # Root project docs
├── INTEGRATION.md                 # Integration guide
└── DEPLOYMENT.md                  # Deployment instructions
```

---

## Run Locally

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

The backend exposes:
- `/api/auth/signup`
- `/api/auth/login`
- `/api/auth/refresh`
- `/api/auth/profile`
- `/api/conversations`
- `/api/messages`
- `/api/users/search`
- `/api/health`

Socket.IO handles real-time events for authentication, conversation rooms, messaging, typing indicators, and online presence.

### Frontend

```bash
cd realtime-morse-frontend
npm install
npm run dev
```

Open `http://localhost:8080`.

The frontend supports keyboard and mic Morse input, text encoding, live decoding, and chat interactions.

---

## Deployment

See `DEPLOYMENT.md` for production guidance, including:
- Docker / Docker Compose
- Heroku
- AWS Elastic Beanstalk / S3 + CloudFront
- Railway

---

## Troubleshooting

- **Frontend cannot reach backend**: verify `VITE_API_URL`, backend port, and CORS origins.
- **Auth token errors**: ensure `JWT_SECRET_KEY` is configured and backend restarted.
- **Socket.IO issues**: confirm backend is running and `SOCKET_URL` matches frontend expectations.
- **Database permission errors**: check `DATABASE_URL` and SQLite file access.
- **Tap detection is noisy**: use the notebook demo to recalibrate and adjust `SPIKE_FACTOR`, `GAIN`, and timing thresholds.

---

## Related Docs

- `backend/README.md` — backend API and route documentation
- `realtime-morse-frontend/README.md` — frontend setup and development guide
- `INTEGRATION.md` — frontend/backend integration notes
- `DEPLOYMENT.md` — deployment documentation

---

## Notes

- `build.ipynb` provides a prototype/demo workflow for audio recording, feature extraction, and ML model calibration.
- The frontend and backend can run independently for development and production.
- Use `docker-compose.yml` for the simplest local setup.
