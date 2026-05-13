// src/store/authStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, AuthState, LoginData, SignupData } from '../types/auth';
import { authService } from '../services/api/auth';

interface AuthStore extends AuthState {
  login: (data: LoginData) => Promise<void>;
  signup: (data: SignupData) => Promise<void>;
  logout: () => void;
  refreshAuthToken: () => Promise<void>;
  setLoading: (loading: boolean) => void;
  initializeAuth: () => void;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (data: LoginData) => {
        set({ isLoading: true });
        try {
          const response = await authService.login(data);
          const token = response.token;
          const refreshToken = response.refresh_token;

          localStorage.setItem('token', token);
          localStorage.setItem('refresh_token', refreshToken);

          set({
            user: response.user,
            token,
            refreshToken,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      signup: async (data: SignupData) => {
        set({ isLoading: true });
        try {
          const response = await authService.signup(data);
          const token = response.token;
          const refreshToken = response.refresh_token;

          localStorage.setItem('token', token);
          localStorage.setItem('refresh_token', refreshToken);

          set({
            user: response.user,
            token,
            refreshToken,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      logout: () => {
        localStorage.removeItem('token');
        localStorage.removeItem('refresh_token');
        authService.logout();
        set({
          user: null,
          token: null,
          refreshToken: null,
          isAuthenticated: false,
        });
      },

      refreshAuthToken: async () => {
        try {
          const response = await authService.refreshToken();
          const newToken = response.token;

          localStorage.setItem('token', newToken);
          set({ token: newToken });
        } catch (error) {
          get().logout();
          throw error;
        }
      },

      setLoading: (isLoading: boolean) => set({ isLoading }),

      initializeAuth: () => {
        const token = localStorage.getItem('token');
        const refreshToken = localStorage.getItem('refresh_token');

        if (token && refreshToken) {
          set({
            token,
            refreshToken,
            isAuthenticated: true,
          });
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
