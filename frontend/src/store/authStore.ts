/**
 * Authentication store
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { AuthState, User, TokenResponse } from '@/types/auth';
import { getApiClient } from '@/lib/api';

interface AuthStore extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => void;
  setTokens: (accessToken: string, refreshToken: string) => void;
  setUser: (user: User | null) => void;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isLoading: false,
      error: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          const api = getApiClient();
          const response = await api.post<TokenResponse>('/api/v1/auth/login', {
            email,
            password,
          });
          
          set({
            accessToken: response.data.access_token,
            refreshToken: response.data.refresh_token,
            isLoading: false,
          });

          // Fetch user info
          const userResponse = await api.get('/api/v1/auth/me');
          set({ user: userResponse.data });
        } catch (error: any) {
          const detail = error.response?.data?.detail;
          const message = typeof detail === 'string'
            ? detail
            : Array.isArray(detail)
              ? detail.map((d: any) => d.msg).join(', ')
              : 'Login failed';
          set({
            error: message,
            isLoading: false,
          });
          throw error;
        }
      },

      register: async (email: string, password: string, fullName: string) => {
        set({ isLoading: true, error: null });
        try {
          const api = getApiClient();
          const response = await api.post<TokenResponse>('/api/v1/auth/register', {
            email,
            password,
            full_name: fullName,
          });
          
          set({
            accessToken: response.data.access_token,
            refreshToken: response.data.refresh_token,
            isLoading: false,
          });

          // Fetch user info
          const userResponse = await api.get('/api/v1/auth/me');
          set({ user: userResponse.data });
        } catch (error: any) {
          const detail = error.response?.data?.detail;
          const message = typeof detail === 'string'
            ? detail
            : Array.isArray(detail)
              ? detail.map((d: any) => d.msg).join(', ')
              : 'Registration failed';
          set({
            error: message,
            isLoading: false,
          });
          throw error;
        }
      },

      logout: () => {
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          error: null,
        });
      },

      setTokens: (accessToken: string, refreshToken: string) => {
        set({ accessToken, refreshToken });
      },

      setUser: (user: User | null) => {
        set({ user });
      },
    }),
    {
      name: 'auth-storage',
    }
  )
);
