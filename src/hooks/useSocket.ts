import { useEffect, useRef } from 'react';
import { socketService } from '../services/socket/socket';
import { useAuthStore } from '../store/authStore';

export const useSocket = () => {
  const authState = useAuthStore();
  const hasInitialized = useRef(false);

  useEffect(() => {
    if (hasInitialized.current || !authState.isAuthenticated || !authState.token) {
      return;
    }

    hasInitialized.current = true;

    try {
      socketService.connect();
    } catch (error) {
      console.error('Failed to connect socket:', error);
    }

    return () => {
      socketService.disconnect();
    };
  }, [authState.isAuthenticated, authState.token]);

  return socketService;
};
