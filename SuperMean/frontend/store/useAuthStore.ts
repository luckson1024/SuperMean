import { create } from 'zustand';
import axios from 'axios';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  username: string;
  email: string;
  role: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (username: string, email: string, password: string) => Promise<void>;
  clearError: () => void;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

import { StateCreator } from 'zustand';

export const useAuthStore = create<AuthState>(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await axios.post(`${API_URL}/auth/login`, { email, password });
          const { access_token, user } = response.data;
          
          // Set auth headers for future requests
          axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
          
          set({ 
            token: access_token, 
            user, 
            isAuthenticated: true, 
            isLoading: false 
          });
        } catch (error: any) {
          set({ 
            error: error.response?.data?.detail || 'Login failed', 
            isLoading: false,
            isAuthenticated: false,
            token: null,
            user: null
          });
        }
      },

      logout: () => {
        // Remove auth header
        delete axios.defaults.headers.common['Authorization'];
        
        set({ 
          user: null, 
          token: null, 
          isAuthenticated: false, 
          error: null 
        });
      },

      register: async (username: string, email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await axios.post(`${API_URL}/auth/register`, { username, email, password });
          // Auto-login after successful registration
          const loginResponse = await axios.post(`${API_URL}/auth/login`, { email, password });
          const { access_token, user } = loginResponse.data;
          axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
          set({
            token: access_token,
            user,
            isAuthenticated: true,
            isLoading: false,
            error: null
          });
        } catch (error: any) {
          set({
            error: error.response?.data?.detail || 'Registration failed',
            isLoading: false
          });
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage', // name of the item in the storage
      getStorage: () => localStorage, // (optional) by default, 'localStorage' is used
    }
  ) as StateCreator<AuthState, [], []>
);