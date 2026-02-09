'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiClient } from '@/lib/api';

interface AuthContextType {
  user: any;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: () => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<any>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    // Check for existing token in localStorage on mount
    const storedAuth = localStorage.getItem('auth');
    if (storedAuth) {
      try {
        const authData = JSON.parse(storedAuth);
        const storedToken = authData.token;
        if (storedToken) {
          setToken(storedToken);
          // In a real app, you'd decode the token or make an API call to get user info
          // For now, we'll just set a mock user
          // In a real implementation, you'd make an API call to get user details
          try {
            // const userData = await apiClient.getProfile();
            // setUser(userData);
            setUser({ id: 'mock-user-id', email: 'mock@example.com' });
          } catch (error) {
            console.error('Failed to get user profile:', error);
            // Token might be invalid, so clear it
            localStorage.removeItem('auth');
            setToken(null);
            setUser(null);
          }
        }
      } catch (e) {
        console.error('Failed to parse auth data:', e);
        localStorage.removeItem('auth');
      }
    }
  }, []);

  const login = async (email: string, password: string) => {
    try {
      // Make actual API call to login
      const response = await apiClient.login(email, password);

      // Set token in localStorage and state
      setToken(response.token);
      localStorage.setItem('auth', JSON.stringify({ token: response.token }));

      // Set user data
      setUser(response.user);
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const signup = async (email: string, password: string) => {
    try {
      // Make actual API call to signup
      const response = await apiClient.signup(email, password);

      // Set token in localStorage and state
      setToken(response.token);
      localStorage.setItem('auth', JSON.stringify({ token: response.token }));

      // Set user data
      setUser(response.user);
    } catch (error) {
      console.error('Signup failed:', error);
      throw error;
    }
  };

  const logout = () => {
    // Make API call to logout (optional, depending on backend implementation)
    // await apiClient.logout();

    // Clear token from localStorage and state
    setToken(null);
    setUser(null);
    localStorage.removeItem('auth');
  };

  const isAuthenticated = () => {
    return !!token;
  };

  return (
    <AuthContext.Provider value={{ user, token, login, signup, logout, isAuthenticated }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}