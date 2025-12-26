import React, { useState, useEffect } from 'react';
import { Save, RotateCcw, AlertCircle, Info, TrendingUp, Zap, Target, DollarSign, Clock, Shield } from 'lucide-react';

// Bot definitions with all parameters
const BOT_CONFIGS = {
  grid_trading: {
    name: 'Grid Trading Bot',
    icon: '📊',
    color: 'blue',
    exchanges: ['kcex'],
    description: 'Places buy/sell orders in a grid pattern within a price range',
    params: [
      { name: 'symbol', label: 'Trading Pair', type: 'text', default: 'BTC/USDT', required: true },
      { name: 'grid_levels', label: 'Grid Levels', type: 'number', default: 10, min: 3, max: 50, required: true },
      { name: 'lower_price', label: 'Lower Price ($)', type: 'number', default: 25000, min: 0, required: true },
      { name: 'upper_price', label: 'Upper Price ($)', type: 'number', default: 35000, min: 0, required: true },
      { name: 'investment', label: 'Total Investment ($)', type: 'number', default: 1000, min: 100, required: true },
      { name: 'take_profit', label: 'Take Profit (%)', type: 'number', default: 2, min: 0.1, max: 10, step: 0.1 }
    ]
  },
  dca: {
    name: 'DCA (Dollar Cost Averaging)',
    icon: '💰',
    color: 'green',
    exchanges: ['kcex'],
    description: 'Buy fixed amounts at regular intervals regardless of price',
    params: [
      { name: 'symbol', label: 'Trading Pair', type: 'text', default: 'BTC/USDT', required: true },
      { name: 'amount_per_order', label: 'Amount per Order ($)', type: 'number', default: 100, min: 10, required: true },
      { name: 'interval_hours', label: 'Interval (hours)', type: 'number', default: 24, min: 1, max: 168, required: true },
      { name: 'total_orders', label: 'Total Orders', type: 'number', default: 30, min: 1, max: 365 },
      { name: 'max_investment', label: 'Max Investment ($)', type: 'number', default: 3000, min: 100 }
    ]
  },
  momentum: {
    name: 'Momentum Trading Bot',
    icon: '🚀',
    color: 'purple',
    exchanges: ['kcex'],
    description: 'Trade based on price momentum and trend strength',
    params: [
      { name: 'symbol', label: 'Trading Pair', type: 'text', default: 'ETH/USDT', required: true },
      { name: 'timeframe', label: 'Timeframe', type: 'select', default: '1h', options: ['5m', '15m', '1h', '4h', '1d'], required: true },
      { name: 'momentum_period', label: 'Momentum Period', type: 'number', default: 14, min: 5, max: 50, required: true },
      { name: 'entry_threshold', label: 'Entry Threshold (%)', type: 'number', default: 5, min: 1, max: 20, step: 0.5 },
      { name: 'stop_loss', label: 'Stop Loss (%)', type: 'number', default: 3, min: 0.5, max: 10, step: 0.5 },
      { name: 'take_profit', label: 'Take Profit (%)', type: 'number', default: 8, min: 1, max: 30, step: 0.5 },
      { name: 'position_size', label: 'Position Size ($)', type: 'number', default: 500, min: 50, required: true }
    ]
  },
  mean_reversion: {
    name: 'Mean Reversion Bot',
    icon: '📉',
    color: 'orange',
    exchanges: ['kcex'],
    description: 'Buy when price deviates below average, sell when above',
    params: [
      { name: 'symbol', label: 'Trading Pair', type: 'text', default: 'BTC/USDT', required: true },
      { name: 'lookback_period', label: 'Lookback Period', type: 'number', default: 20, min: 5, max: 100, required: true },
      { name: 'std_dev_entry', label: 'Std Dev Entry', type: 'number', default: 2, min: 1, max: 4, step: 0.1 },
      { name: 'std_dev_exit', label: 'Std Dev Exit', type: 'number', default: 0.5, min: 0.1, max: 2, step: 0.1 },
      { name: 'position_size', label: 'Position Size ($)', type: 'number', default: 500, min: 50, required: true }
    ]
  },
  aggressive_scalper: {
    name: 'Aggressive Scalper Bot',
    icon: '⚡',
    color: 'red',
    exchanges: ['kcex'],
    description: 'High-frequency small profit trades with tight spreads',
    params: [
      { name: 'symbol', label: 'Trading Pair', type: 'text', default: 'BTC/USDT', required: true },
      { name: 'profit_target', label: 'Profit Target (%)', type: 'number', default: 0.5, min: 0.1, max: 2, step: 0.1, required: true },
      { name: 'stop_loss', label: 'Stop Loss (%)', type: 'number', default: 0.3, min: 0.1, max: 1, step: 0.1, required: true },
      { name: 'max_trades_per_day', label: 'Max Trades/Day', type: 'number', default: 50, min: 10, max: 200 },
      { name: 'position_size', label: 'Position Size ($)', type: 'number', default: 200, min: 50, required: true }
    ]
  },
  arbitrage: {
    name: 'CEX-DEX Arbitrage Bot',
    icon: '🔄',
    color: 'teal',
    exchanges: ['kcex', 'hyperliquid', 'uniswap'],
    description: 'Profit from price differences between centralized and decentralized exchanges',
    params: [
      { name: 'token', label: 'Token', type: 'text', default: 'WETH', required: true },
      { name: 'cex_exchange', label: 'CEX Exchange', type: 'select', default: 'kcex', options: ['kcex', 'hyperliquid'], required: true },
      { name: 'dex_exchange', label: 'DEX Exchange', type: 'select', default: 'uniswap', options: ['uniswap', 'hyperliquid'], required: true },
      { name: 'min_profit', label: 'Min Profit (%)', type: 'number', default: 1, min: 0.1, max: 5, step: 0.1, required: true },
      { name: 'max_slippage', label: 'Max Slippage (%)', type: 'number', default: 0.5, min: 0.1, max: 2, step: 0.1 },
      { name: 'trade_amount', label: 'Trade Amount ($)', type: 'number', default: 500, min: 100, required: true }
    ]
  },
  futures_long_short: {
    name: 'Futures Long/Short Bot',
    icon: '📈',
    color: 'indigo',
    exchanges: ['hyperliquid'],
    description: 'Trade futures with leverage based on trend signals',
    params: [
      { name: 'symbol', label: 'Futures Pair', type: 'text', default: 'BTC-PERP', required: true },
      { name: 'leverage', label: 'Leverage', type: 'number', default: 5, min: 1, max: 20, required: true },
      { name: 'position_size', label: 'Position Size ($)', type: 'number', default: 1000, min: 100, required: true },
      { name: 'stop_loss', label: 'Stop Loss (%)', type: 'number', default: 2, min: 0.5, max: 10, step: 0.5 },
      { name: 'take_profit', label: 'Take Profit (%)', type: 'number', default: 5, min: 1, max: 20, step: 0.5 },
      { name: 'timeframe', label: 'Timeframe', type: 'select', default: '15m', options: ['5m', '15m', '1h', '4h'], required: true }
    ]
  },
  market_making: {
    name: 'Market Making Bot',
    icon: '💱',
    color: 'pink',
    exchanges: ['kcex', 'hyperliquid'],
    description: 'Provide liquidity by placing bid/ask orders around market price',
    params: [
      { name: 'symbol', label: 'Trading Pair', type: 'text', default: 'ETH/USDT', required: true },
      { name: 'spread', label: 'Spread (%)', type: 'number', default: 0.5, min: 0.1, max: 2, step: 0.1, required: true },
      { name: 'order_size', label: 'Order Size ($)', type: 'number', default: 300, min: 50, required: true },
      { name: 'num_orders', label: 'Orders per Side', type: 'number', default: 5, min: 1, max: 20 },
      { name: 'inventory_target', label: 'Inventory Target ($)', type: 'number', default: 1000, min: 100 }
    ]
  },
  swing_trading: {
    name: 'Swing Trading Bot',
    icon: '🎯',
    color: 'cyan',
    exchanges: ['kcex'],
    description: 'Medium-term trades holding positions for days/weeks',
    params: [
      { name: 'symbol', label: 'Trading Pair', type: 'text', default: 'BTC/USDT', required: true },
      { name: 'timeframe', label: 'Timeframe', type: 'select', default: '4h', options: ['1h', '4h', '1d'], required: true },
      { name: 'rsi_oversold', label: 'RSI Oversold', type: 'number', default: 30, min: 10, max: 40 },
      { name: 'rsi_overbought', label: 'RSI Overbought', type: 'number', default: 70, min: 60, max: 90 },
      { name: 'stop_loss', label: 'Stop Loss (%)', type: 'number', default: 5, min: 1, max: 15, step: 0.5 },
      { name: 'take_profit', label: 'Take Profit (%)', type: 'number', default: 15, min: 5, max: 50, step: 1 },
      { name: 'position_size', label: 'Position Size ($)', type: 'number', default: 1000, min: 100, required: true }
    ]
  },
  trend_following: {
    name: 'Trend Following Bot',
    icon: '📊',
    color: 'emerald',
    exchanges: ['kcex', 'hyperliquid'],
    description: 'Follow strong market trends using moving averages',
    params: [
      { name: 'symbol', label: 'Trading Pair', type: 'text', default: 'ETH/USDT', required: true },
      { name: 'fast_ma', label: 'Fast MA Period', type: 'number', default: 20, min: 5, max: 50, required: true },
      { name: 'slow_ma', label: 'Slow MA Period', type: 'number', default: 50, min: 20, max: 200, required: true },
      { name: 'timeframe', label: 'Timeframe', type: 'select', default: '1h', options: ['15m', '1h', '4h', '1d'], required: true },
      { name: 'stop_loss', label: 'Stop Loss (%)', type: 'number', default: 4, min: 1, max: 10, step: 0.5 },
      { name: 'position_size', label: 'Position Size ($)', type: 'number', default: 800, min: 100, required: true }
    ]
  }
};

// Risk presets
const RISK_PRESETS = {
  conservative: { name: 'Conservative', multiplier: 0.5, color: 'green' },
  moderate: { name: 'Moderate', multiplier: 1, color: 'blue' },
  aggressive: { name: 'Aggressive', multiplier: 2, color: 'red' }
};

const BotConfiguration = ({ botId, onSave, onCancel }) => {
  const [config, setConfig] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState({});
  const [riskPreset, setRiskPreset] = useState('moderate');

  const botConfig = BOT_CONFIGS[botId];

  useEffect(() => {
    loadConfig();
  }, [botId]);

  const loadConfig = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/bots/${botId}/config`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });

      if (response.ok) {
        const data = await response.json();
        setConfig(data.config || getDefaultConfig());
      } else {
        setConfig(getDefaultConfig());
      }
    } catch (error) {
      console.error('Failed to load config:', error);
      setConfig(getDefaultConfig());
    } finally {
      setLoading(false);
    }
  };

  const getDefaultConfig = () => {
    const defaults = {};
    botConfig.params.forEach(param => {
      defaults[param.name] = param.default;
    });
    return defaults;
  };

  const validateConfig = () => {
    const newErrors = {};
    
    botConfig.params.forEach(param => {
      if (param.required && !config[param.name]) {
        newErrors[param.name] = 'Required field';
      }
      
      if (param.type === 'number' && config[param.name]) {
        const value = parseFloat(config[param.name]);
        if (param.min !== undefined && value < param.min) {
          newErrors[param.name] = `Minimum value: ${param.min}`;
        }
        if (param.max !== undefined && value > param.max) {
          newErrors[param.name] = `Maximum value: ${param.max}`;
        }
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = async () => {
    if (!validateConfig()) return;

    try {
      setSaving(true);
      const response = await fetch(`/api/bots/${botId}/config`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ config })
      });

      if (response.ok) {
        onSave?.(config);
      } else {
        const data = await response.json();
        alert(data.error || 'Failed to save configuration');
      }
    } catch (error) {
      alert('Connection error');
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    if (confirm('Reset to default values?')) {
      setConfig(getDefaultConfig());
      setErrors({});
    }
  };

  const applyRiskPreset = (preset) => {
    setRiskPreset(preset);
    const multiplier = RISK_PRESETS[preset].multiplier;
    const newConfig = { ...config };

    botConfig.params.forEach(param => {
      if (param.name.includes('stop_loss') || param.name.includes('profit') || param.name.includes('size')) {
        const currentValue = config[param.name] || param.default;
        newConfig[param.name] = Math.round(currentValue * multiplier * 100) / 100;
      }
    });

    setConfig(newConfig);
  };

  const handleInputChange = (paramName, value) => {
    setConfig({ ...config, [paramName]: value });
    setErrors({ ...errors, [paramName]: null });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!botConfig) {
    return (
      <div className="text-center p-8">
        <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <p className="text-gray-600">Bot configuration not found</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-6 text-white">
        <div className="flex items-center gap-4">
          <div className="text-5xl">{botConfig.icon}</div>
          <div>
            <h1 className="text-2xl font-bold">{botConfig.name}</h1>
            <p className="text-blue-100 mt-1">{botConfig.description}</p>
            <div className="flex gap-2 mt-3">
              {botConfig.exchanges.map(ex => (
                <span key={ex} className="bg-white/20 px-3 py-1 rounded text-sm">
                  {ex.toUpperCase()}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Risk Preset Selector */}
      <div className="bg-white border-2 border-gray-200 rounded-lg p-5">
        <div className="flex items-center gap-2 mb-3">
          <Shield className="w-5 h-5 text-gray-600" />
          <h3 className="font-bold text-gray-900">Risk Preset</h3>
        </div>
        <div className="grid grid-cols-3 gap-3">
          {Object.entries(RISK_PRESETS).map(([key, preset]) => (
            <button
              key={key}
              onClick={() => applyRiskPreset(key)}
              className={`p-4 rounded-lg border-2 transition-all ${
                riskPreset === key
                  ? `border-${preset.color}-500 bg-${preset.color}-50`
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className={`font-bold text-${preset.color}-600`}>
                {preset.name}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {key === 'conservative' && 'Lower risk, smaller positions'}
                {key === 'moderate' && 'Balanced risk/reward'}
                {key === 'aggressive' && 'Higher risk, larger positions'}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Configuration Form */}
      <div className="bg-white border-2 border-gray-200 rounded-lg p-6">
        <h3 className="font-bold text-lg mb-4">Configuration Parameters</h3>
        
        <div className="space-y-4">
          {botConfig.params.map((param) => (
            <div key={param.name}>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                {param.label}
                {param.required && <span className="text-red-500 ml-1">*</span>}
              </label>

              {param.type === 'select' ? (
                <select
                  value={config[param.name] || param.default}
                  onChange={(e) => handleInputChange(param.name, e.target.value)}
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    errors[param.name] ? 'border-red-500' : 'border-gray-300'
                  }`}
                >
                  {param.options.map(opt => (
                    <option key={opt} value={opt}>{opt}</option>
                  ))}
                </select>
              ) : (
                <input
                  type={param.type}
                  value={config[param.name] ?? param.default}
                  onChange={(e) => handleInputChange(param.name, e.target.value)}
                  step={param.step}
                  min={param.min}
                  max={param.max}
                  placeholder={`Enter ${param.label.toLowerCase()}`}
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    errors[param.name] ? 'border-red-500' : 'border-gray-300'
                  }`}
                />
              )}

              {errors[param.name] && (
                <p className="text-red-500 text-sm mt-1 flex items-center gap-1">
                  <AlertCircle className="w-4 h-4" />
                  {errors[param.name]}
                </p>
              )}

              {param.min !== undefined && param.max !== undefined && (
                <p className="text-xs text-gray-500 mt-1">
                  Range: {param.min} - {param.max}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Info Box */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex gap-3">
        <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
        <div className="text-sm text-blue-900">
          <p className="font-medium">Configuration Tips:</p>
          <ul className="mt-2 space-y-1">
            <li>• Test with small position sizes first</li>
            <li>• Adjust parameters based on market volatility</li>
            <li>• Monitor performance and iterate</li>
          </ul>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button
          onClick={handleSave}
          disabled={saving}
          className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition font-medium disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {saving ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              Saving...
            </>
          ) : (
            <>
              <Save className="w-5 h-5" />
              Save Configuration
            </>
          )}
        </button>
        
        <button
          onClick={handleReset}
          className="px-6 py-3 border-2 border-gray-300 rounded-lg hover:bg-gray-50 transition flex items-center gap-2"
        >
          <RotateCcw className="w-5 h-5" />
          Reset
        </button>

        {onCancel && (
          <button
            onClick={onCancel}
            className="px-6 py-3 border-2 border-gray-300 rounded-lg hover:bg-gray-50 transition"
          >
            Cancel
          </button>
        )}
      </div>
    </div>
  );
};

export default BotConfiguration;
