// src/services/socket/socket.ts
import { io, Socket } from 'socket.io-client';
import { useAuthStore } from '../../store/authStore';

type AuthCallback = (success: boolean, error?: string) => void;

class SocketService {
  private socket: Socket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private authCallbacks: AuthCallback[] = [];
  private pendingListeners: Record<string, Array<(...args: any[]) => void>> = {};

  connect(): Socket {
    const { token, isAuthenticated } = useAuthStore.getState();

    if (!isAuthenticated || !token) {
      throw new Error('User not authenticated. Please log in first.');
    }

    const socketUrl = import.meta.env.VITE_SOCKET_URL || 'http://localhost:5000';

    this.socket = io(socketUrl, {
      auth: { token },
      transports: ['websocket', 'polling'],
      timeout: 20000,
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: this.maxReconnectAttempts,
    });

    this.setupEventListeners();
    this.flushPendingListeners();

    return this.socket;
  }

  private setupEventListeners() {
    if (!this.socket) return;

    // Connection successful
    this.socket.on('connect', () => {
      console.log('Connected to server');
      this.reconnectAttempts = 0;
    });

    // Authentication successful
    this.socket.on('authenticated', (data: any) => {
      console.log('Socket authenticated:', data);
      this.authCallbacks.forEach((cb) => cb(true));
      this.authCallbacks = [];
    });

    // Authentication failed
    this.socket.on('auth_error', (error: any) => {
      console.error('Socket authentication failed:', error);
      this.authCallbacks.forEach((cb) => cb(false, error?.message));
      this.authCallbacks = [];

      const auth = useAuthStore.getState();
      auth.logout();
      window.location.href = '/login';
    });

    // Disconnected
    this.socket.on('disconnect', (reason) => {
      console.log('Disconnected from server:', reason);
      if (reason === 'io server disconnect') {
        this.reconnect();
      }
    });

    // Connection error
    this.socket.on('connect_error', (error) => {
      console.error('Connection error:', error);
      this.handleReconnect();
    });

    // Reconnection attempt
    this.socket.on('reconnect_attempt', (attempt) => {
      console.log(`Reconnection attempt ${attempt}`);
    });

    // Reconnection failed
    this.socket.on('reconnect_failed', () => {
      console.error('Failed to reconnect after max attempts');
      const auth = useAuthStore.getState();
      auth.logout();
      window.location.href = '/login';
    });
  }

  private handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => {
        if (this.socket) {
          this.socket.connect();
        }
      }, 1000 * this.reconnectAttempts);
    }
  }

  private reconnect() {
    if (this.socket) {
      this.socket.connect();
    }
  }

  onAuthenticated(callback: AuthCallback) {
    this.authCallbacks.push(callback);
  }

  private flushPendingListeners() {
    if (!this.socket) return;

    for (const [event, listeners] of Object.entries(this.pendingListeners)) {
      listeners.forEach((listener) => this.socket!.on(event, listener));
    }

    this.pendingListeners = {};
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  emit(event: string, data?: any) {
    if (this.socket && this.socket.connected) {
      this.socket.emit(event, data);
    } else {
      console.warn('Socket not connected, cannot emit:', event);
    }
  }

  on(event: string, callback: (...args: any[]) => void) {
    if (this.socket) {
      this.socket.on(event, callback);
      return;
    }

    if (!this.pendingListeners[event]) {
      this.pendingListeners[event] = [];
    }
    this.pendingListeners[event].push(callback);
  }

  off(event: string, callback?: (...args: any[]) => void) {
    if (this.socket) {
      if (callback) {
        this.socket.off(event, callback);
      } else {
        this.socket.off(event);
      }
      return;
    }

    if (!callback) {
      delete this.pendingListeners[event];
      return;
    }

    if (this.pendingListeners[event]) {
      this.pendingListeners[event] = this.pendingListeners[event].filter(
        (listener) => listener !== callback
      );
      if (this.pendingListeners[event].length === 0) {
        delete this.pendingListeners[event];
      }
    }
  }

  get isConnected(): boolean {
    return this.socket?.connected || false;
  }

  get socketId(): string | undefined {
    return this.socket?.id;
  }
}

export const socketService = new SocketService();
