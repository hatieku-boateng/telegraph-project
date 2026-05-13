// src/hooks/useAuthInit.ts
import { useEffect } from 'react';
import { useAuthStore } from '../store/authStore';

export const useAuthInit = () => {
  const { initializeAuth, isAuthenticated, token } = useAuthStore();

  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  return {
    isAuthenticated,
    token,
  };
};