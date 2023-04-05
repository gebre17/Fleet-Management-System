/**
 * Custom hook for authentication
 */
import { useCallback } from 'react';
import { useAuthStore } from '@/store/authStore';
import { useRouter } from 'next/navigation';

export const useAuth = () => {
  const router = useRouter();
  const {
    user,
    accessToken,
    refreshToken,
    isLoading,
    error,
    login,
    register,
    logout: logoutStore,
  } = useAuthStore();

  const logout = useCallback(() => {
    logoutStore();
    router.push('/login');
  }, [logoutStore, router]);

  return {
    user,
    accessToken,
    refreshToken,
    isLoading,
    error,
    login,
    register,
    logout,
    isAuthenticated: !!accessToken,
  };
};
