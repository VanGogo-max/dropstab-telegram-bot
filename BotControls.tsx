// frontend/src/components/BotControls.tsx
/**
 * BotControls.tsx - АКТУАЛИЗИРАНА ВЕРСИЯ
 * 
 * ПРОМЕНИ:
 * ❌ МАХНАТО: setInterval polling (fetch на всеки 5s)
 * ❌ МАХНАТО: fetch с localStorage token
 * 
 * ✅ ДОБАВЕНО: useWebSocket за real-time updates
 * ✅ ДОБАВЕНО: apiFetch за API calls
 * ✅ ДОБАВЕНО: Auto-refresh fallback ако WebSocket fail
 */

import React, { useState, useEffect } from 'react';
import { Play, Pause, Square, AlertTriangle, TrendingUp, TrendingDown, DollarSign, Activity, Clock, Zap, Shield, RefreshCw } from 'lucide-react';
import { apiFetch, apiPost } from '../utils/apiClient';
import { useWebSocket } from '../hooks/useWebSocket';

const STATUS_COLORS = {
  running: { bg: 'bg-green-100', text: 'text-green-700', border: 'border-green-500' },
  paused: { bg: 'bg-yellow-100', text: 'text-yellow-700', border: 'border-yellow-500' },
  stopped: { bg: 'bg-gray-100', text: 'text-gray-700', border: 'border-gray-300' },
  error: { bg: 'bg-red-100', text: 'text-red-700', border: 'border-red-500' }
};

interface Metrics {
  pnl: number;
  pnlPercent: number;
  totalTrades: number;
  winRate: number;
  avgTradeTime: number;
  uptime: number;
  lastTrade: string | null;
}

const BotControls = ({ botId, botName, botIcon }: { botId: string; botName: string; botIcon: string }) => {
  const [status, setStatus] = useState<'running' | 'paused' | 'stopped' | 'error'>('stopped');
  const [metrics, setMetrics] = useState<Metrics>({
    pnl: 0,
    pnlPercent: 0,
    totalTrades: 0,
    winRate: 0,
    avgTradeTime: 0,
    uptime: 0,
    lastTrade: null
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showConfirm, setShowConfirm] = useState(false);
  const [confirmAction, setConfirmAction] = useState<string | null>(null);

  /**
   * REAL-TIME UPDATES чрез WebSocket
   * 
   * СТАРО:
   * useEffect(() => {
   *   const interval = setInterval(() => {
   *     fetch('/api/bots/status');
   *   }, 5000);
   * }, []);
   * 
   * НОВО:
   * useWebSocket('/ws/bots/status', callback)
   */
  const { connected: wsConnected } = useWebSocket(
    `/ws/bots/${botId}/status`,
    (data) => {
      console.log('[BotControls] WebSocket update:', data);
      
      if (data.type === 'status') {
        setStatus(data.status);
        if (data.metrics) {
          setMetrics(data.metrics);
        }
      }
      
      if (data.type === 'metrics') {
        setMetrics(prev => ({ ...prev, ...data.metrics }));
      }
    }
  );

  /**
   * Fetch initial status - АКТУАЛИЗИРАНО
   */
  const fetchBotStatus = async () => {
    try {
      // Използваме apiFetch вместо fetch с token
      const response = await apiFetch(`/api/bots/${botId}/status`, {
        method: 'GET'
      });

      if (response.ok) {
        const data = await response.json();
        setStatus(data.status);
        setMetrics(data.metrics || metrics);
        setError(null);
      }
    } catch (err) {
      console.error('[BotControls] Failed to fetch status:', err);
    }
  };

  // Initial load + fallback при WebSocket fail
  useEffect(() => {
    fetchBotStatus();

    // Fallback polling ако WebSocket не работи
    if (!wsConnected) {
      console.log('[BotControls] WebSocket не работи, fallback към polling');
      const interval = setInterval(fetchBotStatus, 10000); // 10s вместо 5s
      return () => clearInterval(interval);
    }
  }, [botId, wsConnected]);

  /**
   * Bot actions - АКТУАЛИЗИРАНО
   */
  const handleAction = async (action: string) => {
    if (action === 'stop' && status === 'running') {
      setConfirmAction(action);
      setShowConfirm(true);
      return;
    }

    await executeAction(action);
  };

  const executeAction = async (action: string) => {
    try {
      setLoading(true);
      setError(null);

      // Използваме apiPost вместо fetch
      const data = await apiPost(`/api/bots/${botId}/${action}`, {});

      setStatus(data.status);
      setShowConfirm(false);
      await fetchBotStatus();

    } catch (err) {
      console.error(`[BotControls] ${action} error:`, err);
      setError(err instanceof Error ? err.message : `Грешка при ${action}`);
    } finally {
      setLoading(false);
    }
  };

  const formatUptime = (seconds: number) => {
    if (!seconds) return '0m';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount);
  };

  const getStatusColor = () => STATUS_COLORS[status] || STATUS_COLORS.stopped;
  const statusColor = getStatusColor();

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header Card */}
      <div className={`border-2 ${statusColor.border} rounded-lg p-6 ${statusColor.bg}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="text-5xl">{botIcon}</div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">{botName}</h2>
              <div className="flex items-center gap-3 mt-2">
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusColor.bg} ${statusColor.text} border ${statusColor.border}`}>
                  {status === 'running' && <Activity className="w-4 h-4 inline mr-1 animate-pulse" />}
                  {status.toUpperCase()}
                </span>
                {status === 'running' && (
                  <span className="text-sm text-gray-600 flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    Uptime: {formatUptime(metrics.uptime)}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* WebSocket Status */}
          <div className="flex items-center gap-2 text-sm">
            <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="text-gray-600">
              {wsConnected ? 'Real-time' : 'Polling'}
            </span>
          </div>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="bg-red-50 border-2 border-red-500 rounded-lg p-4 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-red-900">Грешка</p>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Performance Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* P&L */}
        <div className="bg-white border-2 border-gray-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-gray-600 text-sm mb-2">
            <DollarSign className="w-4 h-4" />
            <span>Total P&L</span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className={`text-2xl font-bold ${
              metrics.pnl >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {formatCurrency(metrics.pnl)}
            </span>
            <span className={`text-sm ${
              metrics.pnlPercent >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              ({metrics.pnlPercent >= 0 ? '+' : ''}{metrics.pnlPercent.toFixed(2)}%)
            </span>
          </div>
          {metrics.pnl >= 0 ? (
            <TrendingUp className="w-5 h-5 text-green-500 mt-2" />
          ) : (
            <TrendingDown className="w-5 h-5 text-red-500 mt-2" />
          )}
        </div>

        {/* Total Trades */}
        <div className="bg-white border-2 border-gray-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-gray-600 text-sm mb-2">
            <Zap className="w-4 h-4" />
            <span>Total Trades</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">{metrics.totalTrades}</div>
          <div className="text-sm text-gray-500 mt-2">
            {metrics.lastTrade ? (
              <>Last: {new Date(metrics.lastTrade).toLocaleTimeString()}</>
            ) : (
              'Няма trades още'
            )}
          </div>
        </div>

        {/* Win Rate */}
        <div className="bg-white border-2 border-gray-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-gray-600 text-sm mb-2">
            <Activity className="w-4 h-4" />
            <span>Win Rate</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">{metrics.winRate.toFixed(1)}%</div>
          <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
            <div 
              className={`h-2 rounded-full ${
                metrics.winRate >= 60 ? 'bg-green-500' : 
                metrics.winRate >= 40 ? 'bg-yellow-500' : 
                'bg-red-500'
              }`}
              style={{ width: `${metrics.winRate}%` }}
            ></div>
          </div>
        </div>

        {/* Avg Trade Time */}
        <div className="bg-white border-2 border-gray-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-gray-600 text-sm mb-2">
            <Clock className="w-4 h-4" />
            <span>Avg Trade Time</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {metrics.avgTradeTime > 0 ? `${Math.round(metrics.avgTradeTime)}m` : 'N/A'}
          </div>
          <div className="text-sm text-gray-500 mt-2">Per position</div>
        </div>
      </div>

      {/* Control Buttons */}
      <div className="bg-white border-2 border-gray-200 rounded-lg p-6">
        <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
          <Shield className="w-5 h-5 text-gray-600" />
          Bot Controls
        </h3>

        <div className="flex gap-3">
          {/* Start Button */}
          {(status === 'stopped' || status === 'paused') && (
            <button
              onClick={() => handleAction('start')}
              disabled={loading}
              className="flex-1 bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <RefreshCw className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  Стартирай
                </>
              )}
            </button>
          )}

          {/* Pause Button */}
          {status === 'running' && (
            <button
              onClick={() => handleAction('pause')}
              disabled={loading}
              className="flex-1 bg-yellow-600 text-white px-6 py-3 rounded-lg hover:bg-yellow-700 transition font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <RefreshCw className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <Pause className="w-5 h-5" />
                  Пауза
                </>
              )}
            </button>
          )}

          {/* Stop Button */}
          {(status === 'running' || status === 'paused') && (
            <button
              onClick={() => handleAction('stop')}
              disabled={loading}
              className="flex-1 bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700 transition font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <RefreshCw className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <Square className="w-5 h-5" />
                  Спри
                </>
              )}
            </button>
          )}

          {/* Refresh Button */}
          <button
            onClick={fetchBotStatus}
            disabled={loading}
            className="px-6 py-3 border-2 border-gray-300 rounded-lg hover:bg-gray-50 transition disabled:opacity-50"
            title="Опресни"
          >
            <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {/* Status Messages */}
        {status === 'stopped' && (
          <div className="mt-4 p-3 bg-gray-50 rounded-lg text-sm text-gray-600">
            💡 Ботът е спрян. Натисни "Стартирай" за да започне търговия.
          </div>
        )}
        {status === 'paused' && (
          <div className="mt-4 p-3 bg-yellow-50 rounded-lg text-sm text-yellow-700">
            ⏸️ Ботът е на пауза. Няма да отваря нови trades. Натисни "Стартирай" за да продължи.
          </div>
        )}
        {status === 'running' && (
          <div className="mt-4 p-3 bg-green-50 rounded-lg text-sm text-green-700">
            ✅ Ботът търгува активно. Следи пазарите за възможности...
          </div>
        )}
      </div>

      {/* Confirmation Modal */}
      {showConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <div className="flex items-center gap-3 mb-4">
              <AlertTriangle className="w-8 h-8 text-red-600" />
              <h3 className="text-xl font-bold">Потвърди Спиране</h3>
            </div>
            
            <p className="text-gray-600 mb-6">
              Сигурен ли си че искаш да спреш този бот? Всички отворени позиции ще бъдат затворени на пазарна цена.
            </p>

            <div className="flex gap-3">
              <button
                onClick={() => executeAction(confirmAction!)}
                disabled={loading}
                className="flex-1 bg-red-600 text-white px-4 py-2.5 rounded-lg hover:bg-red-700 transition font-medium disabled:opacity-50"
              >
                {loading ? 'Спиране...' : 'Да, Спри Бот'}
              </button>
              <button
                onClick={() => {
                  setShowConfirm(false);
                  setConfirmAction(null);
                }}
                disabled={loading}
                className="flex-1 border-2 border-gray-300 px-4 py-2.5 rounded-lg hover:bg-gray-50 transition disabled:opacity-50"
              >
                Отказ
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Safety Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex gap-3">
        <Shield className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
        <div className="text-sm text-blue-900">
          <p className="font-medium">Safety Features:</p>
          <ul className="mt-2 space-y-1">
            <li>• Pause: Спира отварянето на нови trades, запазва съществуващите</li>
            <li>• Stop: Затваря всички позиции и спира бота</li>
            <li>• Emergency stop достъпен 24/7 чрез mobile app</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default BotControls;
