// frontend/src/components/Login.tsx
/**
 * Login.tsx - АКТУАЛИЗИРАНА ВЕРСИЯ
 * 
 * ПРОМЕНИ:
 * ❌ МАХНАТО: localStorage.setItem('token', ...)
 * ❌ МАХНАТО: Direct fetch към /api/auth/login
 * 
 * ✅ ДОБАВЕНО: useAuth() hook
 * ✅ ДОБАВЕНО: Error handling с toast
 * ✅ ДОБАВЕНО: Loading state
 */

import React, { useState } from 'react';
import { useAuth } from '../context/AuthProvider';
import { Mail, Lock, AlertCircle, Loader } from 'lucide-react';

interface LoginProps {
  onSwitchToRegister?: () => void;
}

const Login: React.FC<LoginProps> = ({ onSwitchToRegister }) => {
  const { login } = useAuth();
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Handle Login Submit
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Валидация
    if (!email || !password) {
      setError('Моля, попълнете всички полета');
      return;
    }

    if (!email.includes('@')) {
      setError('Невалиден имейл адрес');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Използваме useAuth hook вместо localStorage
      await login(email, password);
      
      // Success! AuthProvider автоматично обновява UI
      console.log('[Login] Успешен вход');
      
    } catch (err) {
      console.error('[Login] Грешка:', err);
      setError(
        err instanceof Error 
          ? err.message 
          : 'Невалидни credentials. Моля, опитайте отново.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-500 to-purple-600 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl mx-auto mb-4 flex items-center justify-center">
            <span className="text-white text-2xl font-bold">CT</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            CryptoTradeBot Pro
          </h1>
          <p className="text-gray-600">
            Влезте в акаунта си
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border-2 border-red-200 rounded-lg flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-red-800">{error}</div>
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Email Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              Имейл адрес
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                disabled={loading}
                className="w-full pl-10 pr-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition disabled:opacity-50 disabled:cursor-not-allowed"
                autoComplete="email"
              />
            </div>
          </div>

          {/* Password Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              Парола
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                disabled={loading}
                className="w-full pl-10 pr-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition disabled:opacity-50 disabled:cursor-not-allowed"
                autoComplete="current-password"
              />
            </div>
          </div>

          {/* Forgot Password Link */}
          <div className="flex justify-end">
            <button
              type="button"
              className="text-sm text-blue-600 hover:underline"
              disabled={loading}
            >
              Забравена парола?
            </button>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-lg font-medium hover:shadow-lg transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader className="w-5 h-5 animate-spin" />
                Влизане...
              </>
            ) : (
              'Влез'
            )}
          </button>
        </form>

        {/* Register Link */}
        {onSwitchToRegister && (
          <div className="mt-6 text-center">
            <p className="text-gray-600">
              Нямате акаунт?{' '}
              <button
                onClick={onSwitchToRegister}
                className="text-blue-600 font-medium hover:underline"
                disabled={loading}
              >
                Регистрирайте се
              </button>
            </p>
          </div>
        )}

        {/* Demo Account Info */}
        <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <p className="text-xs text-blue-800 text-center">
            🔒 Secure login с httpOnly cookies
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
