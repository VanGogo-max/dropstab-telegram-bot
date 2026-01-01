// frontend/src/components/Register.tsx
/**
 * Register.tsx - АКТУАЛИЗИРАНА ВЕРСИЯ
 * 
 * ПРОМЕНИ:
 * ❌ МАХНАТО: localStorage след регистрация
 * ❌ МАХНАТО: Direct fetch
 * 
 * ✅ ДОБАВЕНО: apiPost от apiClient
 * ✅ ДОБАВЕНО: Redirect към login след success
 */

import React, { useState } from 'react';
import { apiPost } from '../utils/apiClient';
import { Mail, Lock, User, Gift, AlertCircle, Loader, CheckCircle } from 'lucide-react';

interface RegisterProps {
  onSwitchToLogin?: () => void;
}

const Register: React.FC<RegisterProps> = ({ onSwitchToLogin }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    referralCode: '',
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  /**
   * Update form field
   */
  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError(null);
  };

  /**
   * Validate form
   */
  const validateForm = (): string | null => {
    if (!formData.name.trim()) {
      return 'Моля, въведете вашето име';
    }

    if (!formData.email.includes('@')) {
      return 'Невалиден имейл адрес';
    }

    if (formData.password.length < 8) {
      return 'Паролата трябва да е поне 8 символа';
    }

    if (formData.password !== formData.confirmPassword) {
      return 'Паролите не съвпадат';
    }

    return null;
  };

  /**
   * Handle Register Submit
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Валидация
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Използваме apiPost вместо direct fetch
      const response = await apiPost('/api/auth/register', {
        name: formData.name,
        email: formData.email,
        password: formData.password,
        referralCode: formData.referralCode || undefined,
      });

      console.log('[Register] Успешна регистрация:', response);
      
      // Success!
      setSuccess(true);
      
      // Redirect към login след 2 секунди
      setTimeout(() => {
        onSwitchToLogin?.();
      }, 2000);

    } catch (err) {
      console.error('[Register] Грешка:', err);
      setError(
        err instanceof Error
          ? err.message
          : 'Регистрацията не успя. Моля, опитайте отново.'
      );
    } finally {
      setLoading(false);
    }
  };

  // Success Screen
  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-500 to-blue-600 p-4">
        <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8 text-center">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-10 h-10 text-green-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Регистрацията е успешна! 🎉
          </h2>
          <p className="text-gray-600 mb-4">
            Вашият акаунт е създаден. Пренасочване към login...
          </p>
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto"></div>
        </div>
      </div>
    );
  }

  // Register Form
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-500 to-purple-600 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8">
        {/* Header */}
        <div className="text-center mb-6">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl mx-auto mb-4 flex items-center justify-center">
            <span className="text-white text-2xl font-bold">CT</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Създай акаунт
          </h1>
          <p className="text-gray-600">
            Започни автоматизирана търговия днес
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mb-4 p-3 bg-red-50 border-2 border-red-200 rounded-lg flex items-start gap-2">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-red-800">{error}</div>
          </div>
        )}

        {/* Register Form */}
        <form onSubmit={handleSubmit} className="space-y-3">
          {/* Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Пълно име
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={formData.name}
                onChange={(e) => handleChange('name', e.target.value)}
                placeholder="Иван Петров"
                disabled={loading}
                className="w-full pl-10 pr-4 py-2.5 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition disabled:opacity-50"
              />
            </div>
          </div>

          {/* Email */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Имейл адрес
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="email"
                value={formData.email}
                onChange={(e) => handleChange('email', e.target.value)}
                placeholder="your@email.com"
                disabled={loading}
                className="w-full pl-10 pr-4 py-2.5 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition disabled:opacity-50"
              />
            </div>
          </div>

          {/* Password */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Парола
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="password"
                value={formData.password}
                onChange={(e) => handleChange('password', e.target.value)}
                placeholder="Поне 8 символа"
                disabled={loading}
                className="w-full pl-10 pr-4 py-2.5 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition disabled:opacity-50"
              />
            </div>
          </div>

          {/* Confirm Password */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Потвърди парола
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="password"
                value={formData.confirmPassword}
                onChange={(e) => handleChange('confirmPassword', e.target.value)}
                placeholder="Повтори паролата"
                disabled={loading}
                className="w-full pl-10 pr-4 py-2.5 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition disabled:opacity-50"
              />
            </div>
          </div>

          {/* Referral Code */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Referral код (опционално)
            </label>
            <div className="relative">
              <Gift className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={formData.referralCode}
                onChange={(e) => handleChange('referralCode', e.target.value.toUpperCase())}
                placeholder="CRYPTO123"
                disabled={loading}
                className="w-full pl-10 pr-4 py-2.5 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition disabled:opacity-50 uppercase"
              />
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Получи $1 отстъпка с referral код
            </p>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-lg font-medium hover:shadow-lg transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 mt-4"
          >
            {loading ? (
              <>
                <Loader className="w-5 h-5 animate-spin" />
                Регистрация...
              </>
            ) : (
              'Създай акаунт'
            )}
          </button>
        </form>

        {/* Login Link */}
        {onSwitchToLogin && (
          <div className="mt-4 text-center">
            <p className="text-gray-600 text-sm">
              Вече имате акаунт?{' '}
              <button
                onClick={onSwitchToLogin}
                className="text-blue-600 font-medium hover:underline"
                disabled={loading}
              >
                Влезте тук
              </button>
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Register;
