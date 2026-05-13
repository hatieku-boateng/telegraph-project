# ⚡ Telegraph Messenger - Real-Time Morse Chat App

A modern communication platform combining Morse code with real-time messaging. Send messages via keyboard taps, microphone signals, or plain text - all automatically encoded/decoded in real-time.

**[🌐 Live Demo](#) | [📖 API Docs](./backend/README.md) | [🎯 MVP Roadmap](#mvp-roadmap)**

---

## 🚀 Quick Start (MVP)

### Prerequisites
- Node.js 18+
- Python 3.8+
- PostgreSQL (optional, SQLite for MVP)

### Installation

```bash
# Clone repository
git clone <repo-url>
cd telegraph-messenger

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py

# Frontend setup (new terminal)
cd realtime-messenger-frontend
npm install
npm run dev
```

Open `http://localhost:8080` and create an account!

---

## 📋 Table of Contents

- [System Architecture](#system-architecture)
- [Frontend Architecture](#frontend-architecture)
- [Backend Architecture](#backend-architecture)
- [Database Design](#database-design)
- [WebSocket Events](#websocket-events)
- [Component Design](#component-design)
- [UI/UX System](#uiux-system)
- [Feature Breakdown](#feature-breakdown)
- [Development Phases](#development-phases)
- [Recommended Packages](#recommended-packages)
- [Example Implementations](#example-implementations)
- [Deployment Guide](#deployment-guide)
- [Future Scaling](#future-scaling)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Telegraph Messenger                      │
├─────────────────────────────────────────────────────────────┤
│  React Frontend (Vite + TS)    │  Flask Backend (Python)    │
├────────────────────────────────┼────────────────────────────┤
│  • Authentication UI           │  • JWT Auth               │
│  • Real-time Chat              │  • WebSocket Server       │
│  • Morse Input Modes           │  • Morse Processing       │
│  • Signal Visualization        │  • ML Tap Detection       │
│  • Message History             │  • Message Storage        │
│  • PWA Support                 │  • File Uploads           │
└────────────────────────────────┴────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────┐
│                     Database Layer                          │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL / SQLite                                       │
│  • Users • Messages • Conversations • Morse Signals        │
└─────────────────────────────────────────────────────────────┘
```

### Core Technologies

**Frontend:**
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS + shadcn/ui
- Zustand (state management)
- Socket.IO Client (realtime)
- Framer Motion (animations)

**Backend:**
- Flask + Flask-SocketIO
- SQLAlchemy (ORM)
- Flask-JWT-Extended (auth)
- WebSocket support
- ML models (scikit-learn)

**Database:**
- PostgreSQL (production)
- SQLite (development/MVP)

---

## 🎨 Frontend Architecture

### Refactored Structure

```
src/
├── components/
│   ├── auth/              # Login, Signup, Profile
│   │   ├── LoginForm.tsx
│   │   ├── SignupForm.tsx
│   │   └── UserAvatar.tsx
│   ├── chat/              # Chat interface
│   │   ├── ChatWindow.tsx
│   │   ├── MessageBubble.tsx
│   │   ├── MessageInput.tsx
│   │   ├── TypingIndicator.tsx
│   │   └── UserList.tsx
│   ├── morse/             # Morse components
│   │   ├── TelegraphKey.tsx
│   │   ├── AudioDecoder.tsx
│   │   ├── SignalVisualizer.tsx
│   │   ├── MorseWaveform.tsx
│   │   └── TransmissionAnim.tsx
│   ├── layout/            # App layout
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   ├── ChatLayout.tsx
│   │   └── MobileNav.tsx
│   ├── ui/                # shadcn/ui components
│   └── realtime/          # Socket components
│       ├── ConnectionStatus.tsx
│       └── PresenceIndicator.tsx
│
├── hooks/
│   ├── auth/              # Authentication
│   │   ├── useAuth.ts
│   │   └── useProfile.ts
│   ├── chat/              # Chat functionality
│   │   ├── useMessages.ts
│   │   ├── useTyping.ts
│   │   └── usePresence.ts
│   ├── socket/            # WebSocket
│   │   ├── useSocket.ts
│   │   └── useSocketEvents.ts
│   ├── morse/             # Morse processing
│   │   ├── useMorseInput.ts
│   │   ├── useAudioDecoder.ts
│   │   └── useTransmission.ts
│   └── ui/                # UI utilities
│       ├── useTheme.ts
│       └── useResponsive.ts
│
├── services/
│   ├── api/               # REST API
│   │   ├── auth.ts
│   │   ├── messages.ts
│   │   └── users.ts
│   ├── socket/            # WebSocket service
│   │   ├── socket.ts
│   │   └── events.ts
│   └── storage/           # Local storage
│       ├── localStorage.ts
│       └── indexedDB.ts
│
├── store/                 # Global state
│   ├── authStore.ts       # Authentication state
│   ├── chatStore.ts       # Chat state
│   ├── morseStore.ts      # Morse state
│   └── uiStore.ts         # UI state
│
├── pages/                 # Route pages
│   ├── auth/
│   │   ├── Login.tsx
│   │   └── Signup.tsx
│   ├── chat/
│   │   ├── Chat.tsx
│   │   ├── Conversation.tsx
│   │   └── NewChat.tsx
│   ├── settings/
│   │   ├── Profile.tsx
│   │   ├── Preferences.tsx
│   │   └── MorseSettings.tsx
│   └── NotFound.tsx
│
├── types/                 # TypeScript types
│   ├── auth.ts
│   ├── chat.ts
│   ├── morse.ts
│   ├── socket.ts
│   └── api.ts
│
├── utils/                 # Utilities
│   ├── morse.ts           # Morse utilities
│   ├── audio.ts           # Audio processing
│   ├── format.ts          # Text formatting
│   └── validation.ts      # Input validation
│
├── assets/                # Static assets
│   ├── sounds/            # Morse beeps
│   ├── icons/             # Custom icons
│   └── images/            # Images
│
├── App.tsx
├── main.tsx
└── index.css
```

### State Management (Zustand)

```typescript
// authStore.ts
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (credentials: LoginData) => Promise<void>;
  logout: () => void;
  signup: (userData: SignupData) => Promise<void>;
}

// chatStore.ts
interface ChatState {
  conversations: Conversation[];
  activeConversation: string | null;
  messages: Message[];
  onlineUsers: User[];
  sendMessage: (content: string, type: MessageType) => void;
  setActiveConversation: (id: string) => void;
}

// morseStore.ts
interface MorseState {
  currentInput: string;
  decodedText: string;
  isTransmitting: boolean;
  inputMode: 'keyboard' | 'microphone' | 'text';
  addSignal: (signal: MorseSignal) => void;
  clearInput: () => void;
}
```

---

## 🔧 Backend Architecture

### Refactored Structure

```
backend/
├── app.py                 # Main Flask app
├── config.py              # Configuration
├── extensions.py          # Flask extensions
│
├── routes/                # API routes
│   ├── auth.py            # Authentication
│   ├── users.py           # User management
│   ├── messages.py        # Message handling
│   ├── morse.py           # Morse processing
│   └── health.py          # Health checks
│
├── sockets/               # WebSocket events
│   ├── chat.py            # Chat events
│   ├── presence.py        # User presence
│   ├── morse.py           # Morse signals
│   └── connection.py      # Connection handling
│
├── services/              # Business logic
│   ├── auth_service.py    # Authentication
│   ├── chat_service.py    # Chat logic
│   ├── morse_service.py   # Morse processing
│   ├── ml_service.py      # ML models
│   └── notification_service.py
│
├── models/                # Database models
│   ├── user.py            # User model
│   ├── message.py         # Message model
│   ├── conversation.py    # Conversation model
│   ├── morse_signal.py    # Morse signal model
│   └── __init__.py
│
├── auth/                  # Authentication
│   ├── jwt.py             # JWT utilities
│   ├── password.py        # Password hashing
│   └── middleware.py      # Auth middleware
│
├── database/              # Database setup
│   ├── connection.py      # DB connection
│   ├── migrations/        # DB migrations
│   └── seeds.py           # Seed data
│
├── ml/                    # ML models
│   ├── tap_detector.py    # Audio classification
│   ├── signal_processor.py
│   └── model_cache.py
│
├── utils/                 # Utilities
│   ├── morse.py           # Morse utilities
│   ├── audio.py           # Audio processing
│   ├── validation.py      # Input validation
│   └── logger.py          # Logging
│
├── static/                # Static files
├── uploads/               # File uploads
├── tests/                 # Tests
└── requirements.txt
```

### Key Backend Components

**WebSocket Server (Flask-SocketIO):**
```python
# app.py
from flask_socketio import SocketIO, emit, join_room, leave_room

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('join_chat')
def handle_join_chat(data):
    join_room(data['conversation_id'])
    emit('user_joined', {'user_id': data['user_id']}, room=data['conversation_id'])

@socketio.on('send_message')
def handle_send_message(data):
    # Process and broadcast message
    message = chat_service.create_message(data)
    emit('new_message', message, room=data['conversation_id'])
```

**Authentication (Flask-JWT-Extended):**
```python
# auth.py
from flask_jwt_extended import jwt_required, get_jwt_identity

@app.route('/api/messages', methods=['POST'])
@jwt_required()
def send_message():
    current_user = get_jwt_identity()
    # Process message
    return jsonify(message)
```

---

## 🗄️ Database Design

### Schema Overview

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    avatar_initials VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP,
    is_online BOOLEAN DEFAULT FALSE
);

-- Conversations table
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Conversation participants
CREATE TABLE conversation_participants (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    user_id INTEGER REFERENCES users(id),
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(conversation_id, user_id)
);

-- Messages table
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    sender_id INTEGER REFERENCES users(id),
    content TEXT,
    morse_code TEXT,
    message_type VARCHAR(20) DEFAULT 'text', -- 'text', 'morse', 'mixed'
    input_method VARCHAR(20), -- 'keyboard', 'microphone', 'text'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE
);

-- Morse signals (for debugging/analysis)
CREATE TABLE morse_signals (
    id SERIAL PRIMARY KEY,
    message_id INTEGER REFERENCES messages(id),
    signal_sequence TEXT, -- Raw dots/dashes
    audio_features JSONB, -- ML features
    confidence_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes for Performance

```sql
-- Message queries
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at DESC);
CREATE INDEX idx_messages_sender ON messages(sender_id);

-- User presence
CREATE INDEX idx_users_online_last_seen ON users(is_online, last_seen DESC);

-- Conversation participants
CREATE INDEX idx_conversation_participants_user ON conversation_participants(user_id);
```

---

## 🔌 WebSocket Events

### Client → Server Events

```typescript
// Authentication
socket.emit('authenticate', { token: jwtToken });

// Chat
socket.emit('join_conversation', { conversationId: '123' });
socket.emit('leave_conversation', { conversationId: '123' });
socket.emit('send_message', {
  conversationId: '123',
  content: 'HELLO',
  morseCode: '.... . .-.. .-.. ---',
  messageType: 'mixed',
  inputMethod: 'keyboard'
});

// Morse signals
socket.emit('morse_signal', {
  conversationId: '123',
  signal: '.',
  duration: 150,
  isComplete: false
});

// Presence
socket.emit('typing_start', { conversationId: '123' });
socket.emit('typing_stop', { conversationId: '123' });
```

### Server → Client Events

```typescript
// Connection
socket.on('connect', () => console.log('Connected'));
socket.on('disconnect', () => console.log('Disconnected'));

// Authentication
socket.on('authenticated', (data) => { /* success */ });
socket.on('auth_error', (error) => { /* handle error */ });

// Chat
socket.on('message_received', (message) => {
  chatStore.addMessage(message);
});

socket.on('user_joined', (data) => {
  presenceStore.updatePresence(data.userId, true);
});

socket.on('user_left', (data) => {
  presenceStore.updatePresence(data.userId, false);
});

// Morse
socket.on('morse_signal_ack', (data) => {
  morseStore.addSignal(data);
});

socket.on('morse_decoded', (data) => {
  morseStore.setDecodedText(data.text);
});

// Presence
socket.on('user_online', (user) => {
  presenceStore.setOnline(user.id);
});

socket.on('user_offline', (user) => {
  presenceStore.setOffline(user.id);
});

socket.on('typing_indicator', (data) => {
  typingStore.setTyping(data.userId, data.conversationId);
});
```

---

## 🧩 Component Design

### Core Components Hierarchy

```
App
├── AuthLayout
│   ├── LoginPage
│   └── SignupPage
├── ChatLayout
│   ├── Sidebar
│   │   ├── UserList
│   │   ├── ConversationList
│   │   └── SearchUsers
│   └── ChatWindow
│       ├── ChatHeader
│       │   ├── UserAvatar
│       │   ├── PresenceIndicator
│       │   └── ChatActions
│       ├── MessageList
│       │   ├── MessageBubble
│       │   ├── MorseWaveform
│       │   ├── TypingIndicator
│       │   └── MessageReactions
│       ├── MessageInput
│       │   ├── InputModeSelector
│       │   ├── TelegraphKey (keyboard mode)
│       │   ├── AudioDecoder (microphone mode)
│       │   ├── TextInput (text mode)
│       │   └── TransmissionPreview
│       └── SignalVisualizer
└── SettingsLayout
    ├── ProfileSettings
    ├── MorseSettings
    └── AppPreferences
```

### Key Component Examples

**MessageBubble.tsx:**
```tsx
interface MessageBubbleProps {
  message: Message;
  isOwn: boolean;
}

export const MessageBubble = ({ message, isOwn }: MessageBubbleProps) => {
  return (
    <div className={`message-bubble ${isOwn ? 'own' : 'other'}`}>
      <div className="message-header">
        <UserAvatar user={message.sender} size="sm" />
        <span className="timestamp">
          {formatTime(message.createdAt)}
        </span>
      </div>

      {message.morseCode && (
        <div className="morse-code">
          <MorseWaveform code={message.morseCode} />
          <code>{message.morseCode}</code>
        </div>
      )}

      <div className="message-content">
        {message.content}
      </div>

      <div className="message-footer">
        <span className="input-method">
          {getInputMethodIcon(message.inputMethod)}
        </span>
        <MessageReactions message={message} />
      </div>
    </div>
  );
};
```

**MessageInput.tsx:**
```tsx
export const MessageInput = () => {
  const [inputMode, setInputMode] = useState<InputMode>('text');
  const morseInput = useMorseInput();
  const socket = useSocket();

  const handleSend = () => {
    const messageData = {
      conversationId: activeConversation,
      content: morseInput.decodedText,
      morseCode: morseInput.morseCode,
      messageType: inputMode === 'text' ? 'text' : 'morse',
      inputMethod: inputMode
    };

    socket.emit('send_message', messageData);
    morseInput.clear();
  };

  return (
    <div className="message-input">
      <InputModeSelector
        mode={inputMode}
        onChange={setInputMode}
      />

      {inputMode === 'keyboard' && <TelegraphKey />}
      {inputMode === 'microphone' && <AudioDecoder />}
      {inputMode === 'text' && <TextInput />}

      <TransmissionPreview
        morseCode={morseInput.morseCode}
        decodedText={morseInput.decodedText}
      />

      <Button onClick={handleSend} disabled={!morseInput.decodedText}>
        Send
      </Button>
    </div>
  );
};
```

---

## 🎨 UI/UX System

### Design System

**Color Palette:**
```css
:root {
  --bg-primary: #0a0a0a;
  --bg-secondary: #1a1a1a;
  --bg-tertiary: #2a2a2a;
  --text-primary: #ffffff;
  --text-secondary: #cccccc;
  --accent-primary: #00ff88;
  --accent-secondary: #00cccc;
  --border-color: #333333;
  --error: #ff4444;
  --success: #44ff44;
}
```

**Typography:**
- Primary: 'JetBrains Mono', monospace (futuristic)
- Secondary: 'Inter', sans-serif (readable)
- Morse Code: 'Courier New', monospace

**Component Tokens:**
```css
/* Buttons */
.btn-primary {
  background: var(--accent-primary);
  color: var(--bg-primary);
  border-radius: 8px;
  font-weight: 600;
}

.btn-secondary {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
}

/* Message Bubbles */
.message-own {
  background: var(--accent-primary);
  align-self: flex-end;
}

.message-other {
  background: var(--bg-secondary);
  align-self: flex-start;
}

/* Morse Visualization */
.morse-dot {
  width: 8px;
  height: 8px;
  background: var(--accent-primary);
  border-radius: 50%;
  animation: pulse 0.3s ease-in-out;
}

.morse-dash {
  width: 24px;
  height: 8px;
  background: var(--accent-primary);
  border-radius: 4px;
}
```

### Key UI Patterns

**Chat Layout:**
```
┌─────────────────────────────────────────────────┐
│ Header: User Avatar | Name | Online Status     │
├─────────────────────────────────────────────────┤
│ Messages:                                         │
│ ┌─────────────────────────────────────────────┐ │
│ │ Morse: .... . .-.. .-.. ---               │ │
│ │ Decoded: HELLO                            │ │
│ │ Sent via: 🎙️ Microphone                   │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ ┌─────────────────────────────────────────────┐ │
│ │ You: .-.. --- .-..                          │ │
│ │ LOL                                         │ │
│ └─────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────┤
│ Input Mode: [Text] [Keyboard] [Microphone]     │
│                                                 │
│ [Type your message...] [Send]                  │
└─────────────────────────────────────────────────┘
```

**Morse Transmission Animation:**
- Dots: Pulsing circles
- Dashes: Growing bars
- Sound: Telegraph beeps
- Progress: Transmission wave

**Responsive Design:**
- Desktop: Sidebar + chat window
- Tablet: Collapsible sidebar
- Mobile: Bottom navigation, stacked layout

---

## 📋 Feature Breakdown

### Phase 1: Core Authentication (Week 1-2)

**Frontend:**
- [ ] Login/Signup forms with validation
- [ ] JWT token storage
- [ ] Protected routes
- [ ] User avatar generation
- [ ] Guest mode option

**Backend:**
- [ ] User registration endpoint
- [ ] Login endpoint with JWT
- [ ] Password hashing
- [ ] User model
- [ ] Authentication middleware

### Phase 2: Basic Chat System (Week 3-4)

**Frontend:**
- [ ] Socket.IO connection
- [ ] Basic message sending/receiving
- [ ] User list display
- [ ] Conversation selection
- [ ] Message persistence

**Backend:**
- [ ] WebSocket server setup
- [ ] Message creation/storage
- [ ] Conversation management
- [ ] Real-time broadcasting

### Phase 3: Morse Integration (Week 5-6)

**Frontend:**
- [ ] Morse input modes in chat
- [ ] Live Morse decoding
- [ ] Transmission animations
- [ ] Morse sound effects
- [ ] Input mode switching

**Backend:**
- [ ] Morse processing in messages
- [ ] Signal storage
- [ ] Morse validation

### Phase 4: Enhanced UI/UX (Week 7-8)

**Frontend:**
- [ ] Modern chat interface
- [ ] Typing indicators
- [ ] Online presence
- [ ] Message reactions
- [ ] Dark theme polish
- [ ] Mobile responsiveness

**Backend:**
- [ ] Presence tracking
- [ ] Typing events
- [ ] Message reactions

### Phase 5: Advanced Features (Week 9-10)

**Frontend:**
- [ ] Message history with pagination
- [ ] Search functionality
- [ ] File uploads
- [ ] Push notifications
- [ ] PWA support

**Backend:**
- [ ] File upload handling
- [ ] Notification system
- [ ] Message search
- [ ] Rate limiting

---

## 📅 Development Phases

### MVP (Month 1)
1. **Week 1:** Authentication system
2. **Week 2:** Basic chat UI and WebSocket connection
3. **Week 3:** Message sending/receiving
4. **Week 4:** Morse input integration

### Beta (Month 2)
5. **Week 5:** Enhanced UI with animations
6. **Week 6:** Mobile responsiveness
7. **Week 7:** Message persistence and history
8. **Week 8:** Testing and bug fixes

### Production (Month 3)
9. **Week 9:** Advanced features (reactions, search)
10. **Week 10:** Performance optimization
11. **Week 11:** Security hardening
12. **Week 12:** Deployment and monitoring

### Timeline Summary
- **MVP:** 4 weeks (basic chat + Morse)
- **Beta:** 4 weeks (polished UI + mobile)
- **Production:** 4 weeks (advanced features + deployment)

---

## 📦 Recommended Packages

### Frontend

**Core:**
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "typescript": "^5.0.0",
  "vite": "^4.3.0"
}
```

**UI & Styling:**
```json
{
  "tailwindcss": "^3.3.0",
  "@radix-ui/react-dialog": "^1.0.0",
  "@radix-ui/react-dropdown-menu": "^2.0.0",
  "lucide-react": "^0.263.0",
  "framer-motion": "^10.12.0",
  "react-hot-toast": "^2.4.0"
}
```

**State & Data:**
```json
{
  "zustand": "^4.3.0",
  "socket.io-client": "^4.7.0",
  "@tanstack/react-query": "^4.29.0",
  "axios": "^1.4.0"
}
```

**Audio & Morse:**
```json
{
  "tone": "^14.7.0",
  "wavesurfer.js": "^7.0.0"
}
```

**Development:**
```json
{
  "@types/react": "^18.2.0",
  "@types/react-dom": "^18.2.0",
  "vitest": "^0.32.0",
  "@testing-library/react": "^14.0.0",
  "eslint": "^8.45.0"
}
```

### Backend

**Core:**
```json
{
  "flask": "^2.3.0",
  "flask-socketio": "^5.3.0",
  "python-socketio": "^5.8.0",
  "flask-cors": "^4.0.0"
}
```

**Database:**
```json
{
  "flask-sqlalchemy": "^3.0.0",
  "psycopg2-binary": "^2.9.0",
  "alembic": "^1.11.0"
}
```

**Authentication:**
```json
{
  "flask-jwt-extended": "^4.5.0",
  "bcrypt": "^4.0.0",
  "pyjwt": "^2.8.0"
}
```

**ML & Audio:**
```json
{
  "scikit-learn": "^1.3.0",
  "numpy": "^1.25.0",
  "sounddevice": "^0.4.0",
  "scipy": "^1.11.0"
}
```

**Utilities:**
```json
{
  "python-dotenv": "^1.0.0",
  "marshmallow": "^3.20.0",
  "redis": "^4.6.0"
}
```

---

## 💡 Example Implementations

### Morse Input Hook

```typescript
// hooks/morse/useMorseInput.ts
import { useState, useCallback } from 'react';
import { useSocket } from '../socket/useSocket';

export const useMorseInput = () => {
  const [morseCode, setMorseCode] = useState('');
  const [decodedText, setDecodedText] = useState('');
  const [isTransmitting, setIsTransmitting] = useState(false);
  const socket = useSocket();

  const addSignal = useCallback((signal: '.' | '-') => {
    const newCode = morseCode + signal;
    setMorseCode(newCode);

    // Send signal to server for real-time decoding
    socket.emit('morse_signal', {
      signal,
      conversationId: activeConversation,
      isComplete: false
    });
  }, [morseCode, socket]);

  const completeLetter = useCallback(() => {
    socket.emit('morse_signal', {
      signal: ' ',
      conversationId: activeConversation,
      isComplete: true
    });
  }, [socket]);

  const clearInput = useCallback(() => {
    setMorseCode('');
    setDecodedText('');
  }, []);

  return {
    morseCode,
    decodedText,
    isTransmitting,
    addSignal,
    completeLetter,
    clearInput
  };
};
```

### Socket Service

```typescript
// services/socket/socket.ts
import { io, Socket } from 'socket.io-client';
import { useAuthStore } from '../../store/authStore';

class SocketService {
  private socket: Socket | null = null;

  connect() {
    const token = useAuthStore.getState().token;

    this.socket = io(process.env.VITE_SOCKET_URL || 'http://localhost:5000', {
      auth: { token },
      transports: ['websocket', 'polling']
    });

    this.socket.on('connect', () => {
      console.log('Connected to server');
    });

    this.socket.on('disconnect', () => {
      console.log('Disconnected from server');
    });

    return this.socket;
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  emit(event: string, data: any) {
    if (this.socket) {
      this.socket.emit(event, data);
    }
  }

  on(event: string, callback: Function) {
    if (this.socket) {
      this.socket.on(event, callback);
    }
  }
}

export const socketService = new SocketService();
```

### Backend Message Handler

```python
# backend/sockets/chat.py
from flask_socketio import emit, join_room, leave_room
from flask_jwt_extended import get_jwt_identity
from ..services import chat_service

def handle_send_message(data):
    user_id = get_jwt_identity()
    conversation_id = data.get('conversation_id')

    # Create message
    message = chat_service.create_message(
        sender_id=user_id,
        conversation_id=conversation_id,
        content=data.get('content'),
        morse_code=data.get('morse_code'),
        message_type=data.get('message_type', 'text'),
        input_method=data.get('input_method', 'text')
    )

    # Broadcast to room
    emit('message_received', message.to_dict(), room=conversation_id)

def handle_join_conversation(data):
    user_id = get_jwt_identity()
    conversation_id = data.get('conversation_id')

    join_room(conversation_id)
    emit('user_joined', {
        'user_id': user_id,
        'conversation_id': conversation_id
    }, room=conversation_id)
```

---

## 🚀 Deployment Guide

### Frontend Deployment

**Vercel (Recommended):**
```bash
npm install -g vercel
vercel --prod
```

**Netlify:**
```bash
npm run build
# Upload dist/ folder to Netlify
```

### Backend Deployment

**Railway:**
```bash
# Create railway.json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python app.py"
  }
}
```

**Render:**
```yaml
# render.yaml
services:
  - type: web
    name: telegraph-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python app.py
```

### Database Setup

**PostgreSQL (Production):**
```bash
# Railway or Supabase
createdb telegraph_messenger
psql telegraph_messenger < schema.sql
```

**SQLite (Development):**
```python
# Automatically created with SQLAlchemy
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///telegraph.db'
db = SQLAlchemy(app)
```

### Environment Variables

**Frontend (.env):**
```env
VITE_API_URL=https://your-backend-api.com
VITE_SOCKET_URL=https://your-socket-server.com
VITE_APP_ENV=production
```

**Backend (.env):**
```env
FLASK_ENV=production
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port
```

### Docker Deployment

**Dockerfile (Backend):**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://db:5432/telegraph
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "8080:80"

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=telegraph
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
```

---

## 🔮 Future Scaling Strategy

### Phase 1: Enhanced Features (3-6 months)
- Group chats
- Message encryption
- File sharing
- Voice messages
- Message reactions
- Advanced Morse features

### Phase 2: Platform Expansion (6-12 months)
- Mobile apps (React Native)
- Desktop app (Electron)
- Hardware integration
- Morse learning mode
- Morse games
- API for third-party integrations

### Phase 3: Enterprise Features (12+ months)
- Team workspaces
- Admin dashboard
- Analytics
- Custom Morse alphabets
- Integration with communication tools
- Morse code education platform

### Technical Scaling Considerations

**Database:**
- Connection pooling
- Read replicas
- Database sharding
- Caching layer (Redis)

**Backend:**
- Microservices architecture
- Load balancing
- Message queues (RabbitMQ)
- Background job processing

**Frontend:**
- Code splitting
- Service workers
- Progressive Web App
- Offline support

**Real-time:**
- Redis adapter for Socket.IO
- Horizontal scaling
- Message persistence
- Connection limits

### Performance Benchmarks

**Target Metrics:**
- Message delivery: <100ms latency
- Concurrent users: 10,000+
- Message throughput: 1,000 msg/sec
- Morse decoding: <50ms
- Mobile app size: <10MB

### Security Roadmap

**Phase 1:**
- End-to-end encryption
- Rate limiting
- Input sanitization
- Secure WebSockets

**Phase 2:**
- Multi-factor authentication
- API key management
- Audit logging
- GDPR compliance

---

## 🎯 MVP Roadmap

### Week 1: Foundation
- [ ] Set up authentication system
- [ ] Create user registration/login
- [ ] Design database schema
- [ ] Initialize WebSocket server

### Week 2: Basic Chat
- [ ] Implement message sending/receiving
- [ ] Create chat UI components
- [ ] Add user presence
- [ ] Set up conversation management

### Week 3: Morse Integration
- [ ] Integrate Morse input modes
- [ ] Add real-time Morse decoding
- [ ] Implement transmission animations
- [ ] Add Morse sound effects

### Week 4: Polish & Test
- [ ] Mobile responsiveness
- [ ] UI/UX improvements
- [ ] Testing and bug fixes
- [ ] Performance optimization

### Success Metrics
- [ ] User registration/login works
- [ ] Real-time messaging functional
- [ ] Morse input modes working
- [ ] Mobile-friendly interface
- [ ] <500ms message latency
- [ ] 99% uptime

---

This comprehensive plan transforms your Morse translator into a modern communication platform. The architecture emphasizes scalability, real-time performance, and an immersive Morse experience while maintaining clean, maintainable code.

Start with the MVP roadmap and iterate based on user feedback. The modular design allows for incremental feature additions without breaking existing functionality.