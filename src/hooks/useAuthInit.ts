import { useEffect } from 'react';
import { useAuthStore } from '../store/authStore';

export const useAuthInit = () => {
  const { initializeAuth } = useAuthStore();

  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);
};
