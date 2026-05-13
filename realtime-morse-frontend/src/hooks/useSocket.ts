// src/hooks/useSocket.ts
import { useEffect, useRef } from 'react';
import { socketService } from '../services/socket/socket';
import { useAuthStore } from '../store/authStore';

export const useSocket = () => {
  const socketRef = useRef<any>(null);
  const { isAuthenticated, token } = useAuthStore();

  useEffect(() => {
    if (isAuthenticated && token && !socketRef.current) {
      try {
        socketRef.current = socketService.connect();
      } catch (error) {
        console.error('Failed to connect socket:', error);
      }
    }

    return () => {
      if (socketRef.current) {
        socketService.disconnect();
        socketRef.current = null;
      }
    };
  }, [isAuthenticated, token]);

  const emit = (event: string, data?: any) => {
    socketService.emit(event, data);
  };

  const on = (event: string, callback: (...args: any[]) => void) => {
    socketService.on(event, callback);
  };

  const off = (event: string, callback?: (...args: any[]) => void) => {
    socketService.off(event, callback);
  };

  return {
    socket: socketRef.current,
    emit,
    on,
    off,
    isConnected: socketService.isConnected,
    socketId: socketService.socketId,
  };
};