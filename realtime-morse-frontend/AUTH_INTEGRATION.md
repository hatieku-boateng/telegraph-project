# Frontend Authentication & Socket Integration Guide

## Setup Overview

This guide shows how to integrate all authentication, JWT token management, route protection, and socket authentication components.

## 1. Initialize App (App.tsx)

```typescript
import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthInit } from './hooks/useAuthInit';
import { useSocket } from './hooks/useSocket';
import { PrivateRoute } from './components/PrivateRoute';
import { useAuthStore } from './store/authStore';

// Pages
import LoginPage from './pages/auth/Login';
import SignupPage from './pages/auth/Signup';
import ChatPage from './pages/chat/Chat';
import SettingsPage from './pages/settings/Profile';

function App() {
  // Initialize auth from localStorage on mount
  useAuthInit();

  // Initialize socket connection when authenticated
  useSocket();

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />

        {/* Protected routes */}
        <Route
          path="/chat"
          element={
            <PrivateRoute>
              <ChatPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <PrivateRoute>
              <SettingsPage />
            </PrivateRoute>
          }
        />

        <Route path="/" element={<Navigate to="/chat" replace />} />
        <Route path="*" element={<Navigate to="/chat" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
```

## 2. Login Component (pages/auth/Login.tsx)

```typescript
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { LoginData } from '../../types/auth';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const navigate = useNavigate();
  const { login, isLoading } = useAuthStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      const data: LoginData = { email, password };
      await login(data);
      navigate('/chat');
    } catch (err: any) {
      setError(err.response?.data?.error || 'Login failed');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900">
      <form onSubmit={handleSubmit} className="w-full max-w-md p-6 bg-gray-800 rounded-lg">
        <h2 className="text-2xl font-bold mb-6 text-green-400">Login</h2>

        {error && <div className="mb-4 p-3 bg-red-900 text-red-200 rounded">{error}</div>}

        <div className="mb-4">
          <label className="block text-sm mb-2">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded text-white"
            required
          />
        </div>

        <div className="mb-6">
          <label className="block text-sm mb-2">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded text-white"
            required
          />
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full py-2 bg-green-500 text-black font-bold rounded hover:bg-green-400 disabled:opacity-50"
        >
          {isLoading ? 'Logging in...' : 'Login'}
        </button>

        <p className="mt-4 text-center text-sm">
          Don't have an account?{' '}
          <a href="/signup" className="text-green-400 hover:underline">
            Sign up
          </a>
        </p>
      </form>
    </div>
  );
}
```

## 3. Chat Component Using Socket (pages/chat/Chat.tsx)

```typescript
import { useEffect, useState } from 'react';
import { socketService } from '../../services/socket/socket';
import { useAuthStore } from '../../store/authStore';

export default function ChatPage() {
  const [messages, setMessages] = useState<any[]>([]);
  const { user } = useAuthStore();

  useEffect(() => {
    if (!socketService.isConnected) {
      return;
    }

    // Listen for incoming messages
    socketService.on('message_received', (message) => {
      setMessages((prev) => [...prev, message]);
    });

    // Join conversations on mount
    socketService.emit('join_conversation', {
      conversation_id: 1, // Replace with actual conversation ID
    });

    return () => {
      socketService.off('message_received');
    };
  }, []);

  const handleSendMessage = (content: string) => {
    socketService.emit('send_message', {
      conversation_id: 1,
      content,
      message_type: 'text',
      input_method: 'text',
    });
  };

  return (
    <div className="h-screen bg-gray-900 text-white">
      <div className="h-full flex flex-col">
        <div className="bg-gray-800 p-4 border-b border-gray-700">
          <h1 className="text-xl font-bold">Chat</h1>
          <p className="text-sm text-gray-400">Welcome, {user?.username}</p>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`p-3 rounded ${msg.sender_id === user?.id ? 'bg-green-700' : 'bg-gray-700'}`}
            >
              <p className="font-semibold text-sm">{msg.sender.username}</p>
              <p>{msg.content}</p>
            </div>
          ))}
        </div>

        <div className="bg-gray-800 p-4 border-t border-gray-700">
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Type a message..."
              className="flex-1 px-4 py-2 bg-gray-700 border border-gray-600 rounded text-white"
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleSendMessage(e.currentTarget.value);
                  e.currentTarget.value = '';
                }
              }}
            />
            <button className="px-4 py-2 bg-green-500 text-black font-bold rounded hover:bg-green-400">
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
```

## 4. API Call Flow

### With automatic JWT handling:

```typescript
// The axios interceptor automatically adds the JWT token
// and handles refresh on 401 errors

import { apiClient } from './services/api/client';

// Automatically includes Bearer token
const response = await apiClient.get('/api/messages');

// On 401, automatically:
// 1. Calls refresh endpoint with refresh_token
// 2. Updates token in store
// 3. Retries original request
// 4. If refresh fails, logs out user
```

## 5. Environment Variables (.env)

```env
VITE_API_URL=http://localhost:5000/api
VITE_SOCKET_URL=http://localhost:5000
VITE_APP_ENV=development
```

## 6. Local Storage Keys

Tokens are automatically stored in localStorage:
- `token` - JWT access token
- `refresh_token` - Refresh token for getting new access tokens

## Authentication Flow Diagram

```
User Login
    ↓
authService.login(email, password)
    ↓
Backend returns: { user, token, refresh_token }
    ↓
authStore.login() stores in localStorage + state
    ↓
useAuthInit() on app mount restores from localStorage
    ↓
apiClient automatically adds Authorization header
    ↓
PrivateRoute checks isAuthenticated
    ↓
useSocket() connects with token in auth handshake
    ↓
socketService 'authenticated' event confirms connection
```

## Socket Authentication Handshake

```typescript
// Client connects with token
socketService.connect()
  → io(url, { auth: { token } })

// Server validates token in backend/sockets/presence.py
@socketio.on('connect', namespace='/')
def handle_connect(auth):
  token = auth['token']
  → verify_jwt(token)
  
// If valid:
emit('authenticated', { user_id, message: 'Connected' })

// If invalid:
emit('auth_error', { message: 'Invalid token' })
→ Frontend logs out, redirects to login
```

## Error Handling

### API Errors:

```typescript
try {
  await login({ email, password });
} catch (error) {
  // 401 → Automatic refresh attempt
  // 403 → Access denied
  // 404 → Not found
  // 5xx → Server error
  console.error(error.response?.data?.error);
}
```

### Socket Auth Errors:

```typescript
socketService.on('auth_error', (error) => {
  console.error('Socket auth failed:', error.message);
  // User is automatically logged out and redirected to /login
});
```

## Testing Authentication

### 1. Login:

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

Response:
```json
{
  "user": { "id": 1, "username": "testuser", "email": "test@example.com" },
  "token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

### 2. Test protected endpoint:

```bash
curl -X GET http://localhost:5000/api/auth/profile \
  -H "Authorization: Bearer eyJ..."
```

### 3. Test socket connection:

```javascript
const socket = io('http://localhost:5000', {
  auth: { token: 'eyJ...' }
});

socket.on('authenticated', (data) => {
  console.log('Socket authenticated:', data);
});

socket.on('auth_error', (error) => {
  console.error('Socket auth failed:', error);
});
```
