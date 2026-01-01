// frontend/src/context/AuthProvider.tsx
/**
 * AuthProvider - Сигурно управление на сесията
 * 
 * ЩО ПРАВИ:
 * - Заменя localStorage JWT с httpOnly cookies
 * - Автоматичен refresh при изтекъл токен
 * - Проверява сесията при reload на страницата
 * - Предоставя login/logout чрез React Context
 * 
 * SECURITY:
 * - JWT никога НЕ се съхранява в localStorage
 * - Cookies са httpOnly, Secure, SameSite=Strict
 * - Автоматичен logout при неуспешен refresh
 */

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';

// Типове
interface User {
  id: string;
  email: string;
  name: string;
  referralCount?: number;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  ensureSession: () => Promise<boolean>;
}

// Създаваме Context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Hook за използване на auth
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth трябва да се използва в рамките на AuthProvider');
  }
  return context;
};

// AuthProvider компонент
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  /**
   * ensureSession - Проверява дали има валидна сесия
   * 
   * FLOW:
   * 1. Опитва /api/auth/me (с httpOnly cookie)
   * 2. Ако е 401 → опитва /api/auth/refresh
   * 3. Ако refresh успее → retry /api/auth/me
   * 4. Ако всичко fail → logout
   */
  const ensureSession = useCallback(async (): Promise<boolean> => {
    try {
      // Опит 1: Провери текущата сесия
      let res = await fetch('/api/auth/me', {
        method: 'GET',
        credentials: 'include', // Изпраща httpOnly cookie
        headers: { 'Accept': 'application/json' },
      });

      // Ако е 401 → токенът е изтекъл
      if (res.status === 401) {
        console.log('[Auth] Токенът е изтекъл, опитвам refresh...');
        
        // Опит 2: Refresh token
        const refreshRes = await fetch('/api/auth/refresh', {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
        });

        if (!refreshRes.ok) {
          console.log('[Auth] Refresh неуспешен, logout');
          setUser(null);
          setLoading(false);
          return false;
        }

        console.log('[Auth] Refresh успешен, retry /api/auth/me');
        
        // Опит 3: Retry оригиналната заявка
        res = await fetch('/api/auth/me', {
          method: 'GET',
          credentials: 'include',
          headers: { 'Accept': 'application/json' },
        });
      }

      // Ако все още не е OK → logout
      if (!res.ok) {
        setUser(null);
        setLoading(false);
        return false;
      }

      // Success! Запазваме user
      const data = await res.json();
      setUser(data.user || null);
      setLoading(false);
      return true;

    } catch (error) {
      console.error('[Auth] Грешка при проверка на сесията:', error);
      setUser(null);
      setLoading(false);
      return false;
    }
  }, []);

  /**
   * login - Вход в системата
   * 
   * ВАЖНО:
   * - Backend трябва да сетне httpOnly cookie при успешен login
   * - Не съхраняваме JWT в localStorage!
   */
  const login = async (email: string, password: string) => {
    setLoading(true);
    
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        credentials: 'include', // Backend ще сетне cookie
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(errorText || 'Login неуспешен');
      }

      const data = await res.json();
      
      // Backend трябва да върне user обект
      setUser(data.user || null);
      
      console.log('[Auth] Login успешен:', data.user?.email);
      
    } catch (error) {
      console.error('[Auth] Login грешка:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  /**
   * logout - Изход от системата
   * 
   * - Изчиства httpOnly cookie на backend
   * - Изчиства user state
   */
  const logout = async () => {
    try {
      await fetch('/api/auth/logout', {
        method: 'POST',
        credentials: 'include',
      });
      
      console.log('[Auth] Logout успешен');
    } catch (error) {
      console.error('[Auth] Logout грешка:', error);
    } finally {
      setUser(null);
    }
  };

  // При зареждане на app → провери дали има сесия
  useEffect(() => {
    console.log('[Auth] Проверка на сесията при старт...');
    ensureSession();
  }, [ensureSession]);

  // Computed value
  const isAuthenticated = !!user;

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated,
        login,
        logout,
        ensureSession,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider;
