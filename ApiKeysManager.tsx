import React, { useState, useEffect } from 'react';
import { Eye, EyeOff, Plus, Trash2, Check, AlertCircle, Lock, RefreshCw } from 'lucide-react';

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
  const [keys, setKeys] = useState({});
  const [showKeys, setShowKeys] = useState({});
  const [validating, setValidating] = useState({});
  const [validated, setValidated] = useState({});
  const [errors, setErrors] = useState({});
  const [editMode, setEditMode] = useState({});
  const [loading, setLoading] = useState(true);

  // Load keys from backend
  useEffect(() => {
    loadApiKeys();
  }, []);

  const loadApiKeys = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/keys', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setKeys(data.keys || {});
        setValidated(data.validated || {});
      }
    } catch (error) {
      console.error('Failed to load API keys:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveKeys = async (exchangeId) => {
    const exchangeKeys = keys[exchangeId];
    if (!exchangeKeys) return;

    // Validate required fields
    const exchange = EXCHANGES.find(e => e.id === exchangeId);
    const missing = exchange.fields.filter(field => !exchangeKeys[field]?.trim());
    
    if (missing.length > 0) {
      setErrors({
        ...errors,
        [exchangeId]: `Missing: ${missing.join(', ')}`
      });
      return;
    }

    try {
      setValidating({ ...validating, [exchangeId]: true });
      setErrors({ ...errors, [exchangeId]: null });

      const response = await fetch('/api/keys', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          exchange: exchangeId,
          keys: exchangeKeys
        })
      });

      const data = await response.json();

      if (response.ok) {
        setValidated({ ...validated, [exchangeId]: true });
        setEditMode({ ...editMode, [exchangeId]: false });
        setTimeout(() => {
          setValidated({ ...validated, [exchangeId]: false });
        }, 3000);
      } else {
        setErrors({ ...errors, [exchangeId]: data.error || 'Validation failed' });
        setValidated({ ...validated, [exchangeId]: false });
      }
    } catch (error) {
      setErrors({ ...errors, [exchangeId]: 'Connection error' });
      setValidated({ ...validated, [exchangeId]: false });
    } finally {
      setValidating({ ...validating, [exchangeId]: false });
    }
  };

  const handleDeleteKeys = async (exchangeId) => {
    if (!confirm(`Delete ${EXCHANGES.find(e => e.id === exchangeId)?.name} API keys?`)) {
      return;
    }

    try {
      const response = await fetch(`/api/keys/${exchangeId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });

      if (response.ok) {
        const newKeys = { ...keys };
        delete newKeys[exchangeId];
        setKeys(newKeys);
        setValidated({ ...validated, [exchangeId]: false });
        setEditMode({ ...editMode, [exchangeId]: false });
      }
    } catch (error) {
      console.error('Failed to delete keys:', error);
    }
  };

  const toggleShowKey = (exchangeId, field) => {
    setShowKeys({
      ...showKeys,
      [`${exchangeId}_${field}`]: !showKeys[`${exchangeId}_${field}`]
    });
  };

  const handleInputChange = (exchangeId, field, value) => {
    setKeys({
      ...keys,
      [exchangeId]: {
        ...(keys[exchangeId] || {}),
        [field]: value
      }
    });
    setErrors({ ...errors, [exchangeId]: null });
  };

  const hasKeys = (exchangeId) => {
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
          Configure exchange API keys for automated trading. All keys are encrypted at rest.
        </p>
      </div>

      {/* Security Notice */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex gap-3">
        <Lock className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
        <div className="text-sm">
          <p className="font-medium text-blue-900">Security Best Practices:</p>
          <ul className="mt-2 space-y-1 text-blue-800">
            <li>• Create API keys with trading permissions only (no withdrawals)</li>
            <li>• Enable IP whitelist if your exchange supports it</li>
            <li>• Use separate API keys for each bot/strategy</li>
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
                          Configured
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
                      Edit
                    </button>
                  )}
                  {isConfigured && (
                    <button
                      onClick={() => handleDeleteKeys(exchange.id)}
                      className="px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition flex items-center gap-2"
                    >
                      <Trash2 className="w-4 h-4" />
                      Delete
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
                            placeholder={`Enter ${field}`}
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
                      <span>API keys validated and saved successfully!</span>
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
                          Validating...
                        </>
                      ) : (
                        <>
                          <Check className="w-4 h-4" />
                          Save & Validate
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
                        Cancel
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
                📚 View {exchange.name} API Documentation →
              </a>
            </div>
          );
        })}
      </div>

      {/* Footer Note */}
      <div className="text-center text-sm text-gray-500 pt-4">
        🔒 All API keys are encrypted using AES-256 before storage
      </div>
    </div>
  );
};

export default ApiKeysManager;
