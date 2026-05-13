// src/types/auth.ts
export interface User {
  id: string;
  username: string;
  email: string;
  avatarInitials: string;
  createdAt: Date;
  lastSeen: Date;
  isOnline: boolean;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface SignupData {
  username: string;
  email: string;
  password: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}