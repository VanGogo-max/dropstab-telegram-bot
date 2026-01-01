// frontend/src/components/ApiKeysManager.tsx
/**
 * ApiKeysManager.tsx - АКТУАЛИЗИРАНА ВЕРСИЯ
 * 
 * ПРОМЕНИ:
 * ❌ МАХНАТО: localStorage.getItem('token')
 * ❌ МАХНАТО: fetch с Authorization header
 * 
 * ✅ ДОБАВЕНО: apiFetch, apiGet, apiPost, apiDelete
 * ✅ ДОБАВЕНО: Auto-retry при 401
 */

import React, { useState, useEffect } from 'react';
import { Eye, EyeOff, Plus, Trash2, Check, AlertCircle, Lock, RefreshCw } from 'lucide-react';
import { apiFetch, apiGet, apiPost, apiDelete } from '../utils/apiClient';

// Exchange configurations
const EXCHANGES = [
  { 
    id: 'kcex', 
    name: 'KCEX', 
    type: 'CEX',
    fields: ['apiKey', 'apiSecret'],
    docs: 'https://www.kucoin.com/support/360015102174'
  },
  { 
    id: 'hyperliquid', 
    name: 'Hyperliquid', 
    type: 'CEX/DEX',
    fields: ['apiKey', 'apiSecret', 'walletAddress'],
    docs: 'https://hyperliquid.gitbook.io/hyperliquid-docs'
  },
  { 
    id: 'uniswap', 
    name: 'Uniswap V3', 
    type: 'DEX',
    fields: ['walletPrivateKey', 'rpcUrl'],
    docs: 'https://docs.uniswap.org/'
  }
];

const ApiKeysManager = () => {
  const [keys, setKeys] = useState<Record<string, any>>({});
  const [showKeys, setShowKeys] = useState<Record<string, boolean>>({});
  const [validating, setValidating] = useState<Record<string, boolean>>({});
  const [validated, setValidated] = useState<Record<string, boolean>>({});
  const [errors, setErrors] = useState<Record<string, string | null>>({});
  const [editMode, setEditMode] = useState<Record<string, boolean>>({});
  const [loading, setLoading] = useState(true);

  // Load keys from backend
  useEffect(() => {
    loadApiKeys();
  }, []);

  /**
   * Load API keys - АКТУАЛИЗИРАНО
   * 
   * СТАРО:
   * const token = localStorage.getItem('token');
   * fetch('/api/keys', { headers: { Authorization: `Bearer ${token}` }})
   * 
   * НОВО:
   * apiGet('/api/keys')
   */
  const loadApiKeys = async () => {
    try {
      setLoading(true);
      
      // Използваме apiGet вместо fetch
      const data = await apiGet('/api/keys');
      
      setKeys(data.keys || {});
      setValidated(data.validated || {});
      
    } catch (error) {
      console.error('[ApiKeys] Failed to load:', error);
      setErrors({ general: 'Неуспешно зареждане на API ключове' });
    } finally {
      setLoading(false);
    }
  };

  /**
   * Save API keys - АКТУАЛИЗИРАНО
   */
  const handleSaveKeys = async (exchangeId: string) => {
    const exchangeKeys = keys[exchangeId];
    if (!exchangeKeys) return;

    // Validate required fields
    const exchange = EXCHANGES.find(e => e.id === exchangeId);
    if (!exchange) return;

    const missing = exchange.fields.filter(field => !exchangeKeys[field]?.trim());
    
    if (missing.length > 0) {
      setErrors({
        ...errors,
        [exchangeId]: `Липсват полета: ${missing.join(', ')}`
      });
      return;
    }

    try {
      setValidating({ ...validating, [exchangeId]: true });
      setErrors({ ...errors, [exchangeId]: null });

      // Използваме apiPost вместо fetch
      const data = await apiPost('/api/keys', {
        exchange: exchangeId,
        keys: exchangeKeys
      });

      if (data.success) {
        setValidated({ ...validated, [exchangeId]: true });
        setEditMode({ ...editMode, [exchangeId]: false });
        
        // Auto-hide success след 3s
        setTimeout(() => {
          setValidated({ ...validated, [exchangeId]: false });
        }, 3000);
      } else {
        throw new Error(data.error || 'Validation failed');
      }

    } catch (error) {
      console.error('[ApiKeys] Save error:', error);
      setErrors({ 
        ...errors, 
        [exchangeId]: error instanceof Error ? error.message : 'Грешка при запазване'
      });
      setValidated({ ...validated, [exchangeId]: false });
    } finally {
      setValidating({ ...validating, [exchangeId]: false });
    }
  };

  /**
   * Delete API keys - АКТУАЛИЗИРАНО
   */
  const handleDeleteKeys = async (exchangeId: string) => {
    const exchange = EXCHANGES.find(e => e.id === exchangeId);
    if (!confirm(`Изтрий ${exchange?.name} API ключове?`)) {
      return;
    }

    try {
      // Използваме apiDelete вместо fetch
      await apiDelete(`/api/keys/${exchangeId}`);

      const newKeys = { ...keys };
      delete newKeys[exchangeId];
      setKeys(newKeys);
      setValidated({ ...validated, [exchangeId]: false });
      setEditMode({ ...editMode, [exchangeId]: false });

    } catch (error) {
      console.error('[ApiKeys] Delete error:', error);
      alert('Неуспешно изтриване на ключове');
    }
  };

  const toggleShowKey = (exchangeId: string, field: string) => {
    setShowKeys({
      ...showKeys,
      [`${exchangeId}_${field}`]: !showKeys[`${exchangeId}_${field}`]
    });
  };

  const handleInputChange = (exchangeId: string, field: string, value: string) => {
    setKeys({
      ...keys,
      [exchangeId]: {
        ...(keys[exchangeId] || {}),
        [field]: value
      }
    });
    setErrors({ ...errors, [exchangeId]: null });
  };

  const hasKeys = (exchangeId: string) => {
    return keys[exchangeId] && Object.keys(keys[exchangeId]).length > 0;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="border-b pb-4">
        <h1 className="text-2xl font-bold text-gray-900">API Keys Manager</h1>
        <p className="text-gray-600 mt-1">
          Конфигурирай API ключове за автоматизирана търговия. Всички ключове са криптирани.
        </p>
      </div>

      {/* Security Notice */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex gap-3">
        <Lock className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
        <div className="text-sm">
          <p className="font-medium text-blue-900">Съвети за сигурност:</p>
          <ul className="mt-2 space-y-1 text-blue-800">
            <li>• Създай API ключове само с trading права (БЕЗ withdrawal)</li>
            <li>• Активирай IP whitelist където е възможно</li>
            <li>• Използвай отделни ключове за всеки бот</li>
          </ul>
        </div>
      </div>

      {/* Exchange Cards */}
      <div className="space-y-4">
        {EXCHANGES.map((exchange) => {
          const isConfigured = hasKeys(exchange.id);
          const isEditing = editMode[exchange.id] || !isConfigured;
          const isValidating = validating[exchange.id];
          const isValidated = validated[exchange.id];
          const error = errors[exchange.id];

          return (
            <div 
              key={exchange.id}
              className={`border-2 rounded-lg p-6 transition-all ${
                isValidated ? 'border-green-500 bg-green-50' : 
                error ? 'border-red-500 bg-red-50' : 
                'border-gray-200 bg-white'
              }`}
            >
              {/* Exchange Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-white font-bold">
                    {exchange.name.substring(0, 2)}
                  </div>
                  <div>
                    <h3 className="font-bold text-lg">{exchange.name}</h3>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">
                        {exchange.type}
                      </span>
                      {isConfigured && !isEditing && (
                        <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded flex items-center gap-1">
                          <Check className="w-3 h-3" />
                          Конфигуриран
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  {isConfigured && !isEditing && (
                    <button
                      onClick={() => setEditMode({ ...editMode, [exchange.id]: true })}
                      className="px-4 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition"
                    >
                      Редактирай
                    </button>
                  )}
                  {isConfigured && (
                    <button
                      onClick={() => handleDeleteKeys(exchange.id)}
                      className="px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition flex items-center gap-2"
                    >
                      <Trash2 className="w-4 h-4" />
                      Изтрий
                    </button>
                  )}
                </div>
              </div>

              {/* Input Fields */}
              {isEditing && (
                <div className="space-y-3">
                  {exchange.fields.map((field) => {
                    const fieldKey = `${exchange.id}_${field}`;
                    const isPassword = field.toLowerCase().includes('secret') || 
                                     field.toLowerCase().includes('private');
                    const value = keys[exchange.id]?.[field] || '';

                    return (
                      <div key={field}>
                        <label className="block text-sm font-medium text-gray-700 mb-1.5">
                          {field.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                        </label>
                        <div className="relative">
                          <input
                            type={isPassword && !showKeys[fieldKey] ? 'password' : 'text'}
                            value={value}
                            onChange={(e) => handleInputChange(exchange.id, field, e.target.value)}
                            placeholder={`Въведи ${field}`}
                            className="w-full px-4 py-2 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
                          />
                          {isPassword && (
                            <button
                              type="button"
                              onClick={() => toggleShowKey(exchange.id, field)}
                              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                            >
                              {showKeys[fieldKey] ? 
                                <EyeOff className="w-5 h-5" /> : 
                                <Eye className="w-5 h-5" />
                              }
                            </button>
                          )}
                        </div>
                      </div>
                    );
                  })}

                  {/* Error Message */}
                  {error && (
                    <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 p-3 rounded-lg">
                      <AlertCircle className="w-4 h-4 flex-shrink-0" />
                      <span>{error}</span>
                    </div>
                  )}

                  {/* Success Message */}
                  {isValidated && (
                    <div className="flex items-center gap-2 text-sm text-green-600 bg-green-50 p-3 rounded-lg">
                      <Check className="w-4 h-4 flex-shrink-0" />
                      <span>API ключове валидирани и запазени успешно!</span>
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div className="flex gap-3 pt-2">
                    <button
                      onClick={() => handleSaveKeys(exchange.id)}
                      disabled={isValidating}
                      className="flex-1 bg-blue-600 text-white px-4 py-2.5 rounded-lg hover:bg-blue-700 transition font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    >
                      {isValidating ? (
                        <>
                          <RefreshCw className="w-4 h-4 animate-spin" />
                          Валидиране...
                        </>
                      ) : (
                        <>
                          <Check className="w-4 h-4" />
                          Запази & Валидирай
                        </>
                      )}
                    </button>
                    {isConfigured && (
                      <button
                        onClick={() => {
                          setEditMode({ ...editMode, [exchange.id]: false });
                          setErrors({ ...errors, [exchange.id]: null });
                        }}
                        className="px-4 py-2.5 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
                      >
                        Отказ
                      </button>
                    )}
                  </div>
                </div>
              )}

              {/* Configured View */}
              {isConfigured && !isEditing && (
                <div className="space-y-2">
                  {exchange.fields.map((field) => (
                    <div key={field} className="flex justify-between items-center py-2">
                      <span className="text-sm text-gray-600">
                        {field.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                      </span>
                      <span className="text-sm font-mono text-gray-400">
                        ••••••••••••
                      </span>
                    </div>
                  ))}
                </div>
              )}

              {/* Documentation Link */}
              <a
                href={exchange.docs}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-blue-600 hover:underline mt-4 inline-block"
              >
                📚 Виж {exchange.name} документация →
              </a>
            </div>
          );
        })}
      </div>

      {/* Footer Note */}
      <div className="text-center text-sm text-gray-500 pt-4">
        🔒 Всички API ключове са криптирани с AES-256 преди съхранение
      </div>
    </div>
  );
};

export default ApiKeysManager;
