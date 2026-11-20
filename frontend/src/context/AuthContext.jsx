import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiService } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem('auth_user');
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  });
  const [token, setToken] = useState(() => localStorage.getItem('access_token') || null);
  const [loading, setLoading] = useState(true);

  // Validate session on mount or token change
  useEffect(() => {
    let isMounted = true;

    const verifySession = async () => {
      const savedToken = localStorage.getItem('access_token');
      if (!savedToken) {
        if (isMounted) {
          setUser(null);
          setToken(null);
          setLoading(false);
        }
        return;
      }

      try {
        const userData = await apiService.getCurrentUser();
        if (isMounted) {
          setUser(userData);
          setToken(savedToken);
          localStorage.setItem('auth_user', JSON.stringify(userData));
        }
      } catch (err) {
        // Token invalid or expired
        if (isMounted) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('auth_user');
          setUser(null);
          setToken(null);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    verifySession();

    // Listen for unauthorized 401 events dispatched from axios
    const handleUnauthorized = () => {
      setUser(null);
      setToken(null);
    };
    window.addEventListener('auth:unauthorized', handleUnauthorized);

    return () => {
      isMounted = false;
      window.removeEventListener('auth:unauthorized', handleUnauthorized);
    };
  }, []);

  const login = async (emailOrUsername, password, rememberMe = true) => {
    const res = await apiService.loginUser({
      email_or_username: emailOrUsername,
      password,
    });

    const accessToken = res.access_token;
    const userData = res.user;

    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('auth_user', JSON.stringify(userData));
    setToken(accessToken);
    setUser(userData);

    return userData;
  };

  const register = async (userData) => {
    const res = await apiService.registerUser(userData);

    const accessToken = res.access_token;
    const userProfile = res.user;

    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('auth_user', JSON.stringify(userProfile));
    setToken(accessToken);
    setUser(userProfile);

    return userProfile;
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('auth_user');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        isAuthenticated: !!token && !!user,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
