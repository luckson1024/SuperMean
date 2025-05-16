import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAuthStore } from '../store';

/**
 * Custom hook for handling authentication-related functionality
 * Provides simplified access to auth state and methods
 */
export const useAuth = () => {
  const router = useRouter();
  const { 
    user, 
    token, 
    isAuthenticated, 
    isLoading, 
    error, 
    login, 
    logout, 
    register, 
    clearError 
  } = useAuthStore();

  // Redirect to login if not authenticated
  const requireAuth = () => {
    useEffect(() => {
      if (!isLoading && !isAuthenticated) {
        router.push('/');
      }
    }, [isAuthenticated, isLoading]);
  };

  // Redirect to dashboard if already authenticated
  const redirectIfAuthenticated = () => {
    useEffect(() => {
      if (isAuthenticated) {
        router.push('/dashboard');
      }
    }, [isAuthenticated]);
  };

  return {
    user,
    token,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout,
    register,
    clearError,
    requireAuth,
    redirectIfAuthenticated
  };
};