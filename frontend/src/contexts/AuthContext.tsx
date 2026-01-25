import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';
import type { User, SignupResponse, LoginResponse, AuthTokenResponse } from '@/types/auth';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  signup: (name: string, email: string, password: string) => Promise<{ success: boolean; error?: string; isNewUser?: boolean }>;
  logout: () => void;
  updateUser: (userData: Partial<User>) => void;
  checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const checkAuth = useCallback(async () => {
    const storedToken = localStorage.getItem('access_token');
    const storedUser = localStorage.getItem('user');

    if (!storedToken) {
      setIsLoading(false);
      return;
    }

    setToken(storedToken);

    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch {
        // Invalid stored user
      }
    }

    // Verify token with backend
    const response = await api.get<User>('/api/auth/me');
    
    if (response.data) {
      setUser(response.data);
      localStorage.setItem('user', JSON.stringify(response.data));
    } else {
      // Token invalid
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      setToken(null);
      setUser(null);
    }

    setIsLoading(false);
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const login = async (email: string, password: string) => {
    const response = await api.post<AuthTokenResponse>('/api/auth/login', {
      email,
      password,
    });

    if (response.error) {
      return { success: false, error: response.error };
    }

    if (response.data) {
      const { access_token, user: userData } = response.data;
      
      localStorage.setItem('access_token', access_token);
      setToken(access_token);

      if (userData) {
        localStorage.setItem('user', JSON.stringify(userData));
        setUser(userData);
      } else {
        // Fetch user data
        const userResponse = await api.get<User>('/api/auth/me');
        if (userResponse.data) {
          localStorage.setItem('user', JSON.stringify(userResponse.data));
          setUser(userResponse.data);
        }
      }

      return { success: true };
    }

    return { success: false, error: 'Login failed' };
  };

  const signup = async (name: string, email: string, password: string) => {
    // Step 1: Create account (returns user data, no token)
    const signupRes = await api.post<SignupResponse>('/api/auth/signup', {
      name,
      email,
      password,
    });

    if (signupRes.error) {
      return { success: false, error: signupRes.error };
    }

    if (!signupRes.data) {
      return { success: false, error: 'Registration failed' };
    }

    // Step 2: Auto-login to get token
    const loginRes = await api.post<LoginResponse>('/api/auth/login', {
      email,
      password,
    });

    if (loginRes.error) {
      return { success: false, error: loginRes.error };
    }

    if (!loginRes.data) {
      return { success: false, error: 'Login after signup failed' };
    }

    // Step 3: Store token
    localStorage.setItem('access_token', loginRes.data.access_token);
    setToken(loginRes.data.access_token);

    // Step 4: Create user object with isOnboarded = false
    const newUser: User = { 
      ...signupRes.data, 
      isOnboarded: false 
    };
    localStorage.setItem('user', JSON.stringify(newUser));
    setUser(newUser);

    return { success: true, isNewUser: true };
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
  };

  const updateUser = (userData: Partial<User>) => {
    if (user) {
      const updatedUser = { ...user, ...userData };
      setUser(updatedUser);
      localStorage.setItem('user', JSON.stringify(updatedUser));
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token && !!user,
        isLoading,
        login,
        signup,
        logout,
        updateUser,
        checkAuth,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};