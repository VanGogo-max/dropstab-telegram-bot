import React, { useState, useEffect } from 'react';
import { Play, Pause, Square, AlertTriangle, TrendingUp, TrendingDown, DollarSign, Activity, Clock, Zap, Shield, RefreshCw } from 'lucide-react';

const STATUS_COLORS = {
  running: { bg: 'bg-green-100', text: 'text-green-700', border: 'border-green-500' },
  paused: { bg: 'bg-yellow-100', text: 'text-yellow-700', border: 'border-yellow-500' },
  stopped: { bg: 'bg-gray-100', text: 'text-gray-700', border: 'border-gray-300' },
  error: { bg: 'bg-red-100', text: 'text-red-700', border: 'border-red-500' }
};

const BotControls = ({ botId, botName, botIcon }) => {
  const [status, setStatus] = useState('stopped');
  const [metrics, setMetrics] = useState({
    pnl: 0,
    pnlPercent: 0,
    totalTrades: 0,
    winRate: 0,
    avgTradeTime: 0,
    uptime: 0,
    lastTrade: null
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showConfirm, setShowConfirm] = useState(false);
  const [confirmAction, setConfirmAction] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    fetchBotStatus();
    
    if (autoRefresh && status === 'running') {
      const interval = setInterval(fetchBotStatus, 5000);
      return () => clearInterval(interval);
    }
  }, [botId, autoRefresh, status]);

  const fetchBotStatus = async () => {
    try {
      const response = await fetch(`/api/bots/${botId}/status`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });

      if (response.ok) {
        const data = await response.json();
        setStatus(data.status);
        setMetrics(data.metrics || metrics);
        setError(null);
      }
    } catch (err) {
      console.error('Failed to fetch status:', err);
    }
  };

  const handleAction = async (action) => {
    if (action === 'stop' && status === 'running') {
      setConfirmAction(action);
      setShowConfirm(true);
      return;
    }

    await executeAction(action);
  };

  const executeAction = async (action) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/bots/${botId}/${action}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      const data = await response.json();

      if (response.ok) {
        setStatus(data.status);
        setShowConfirm(false);
        await fetchBotStatus();
      } else {
        setError(data.error || `Failed to ${action} bot`);
      }
    } catch (err) {
      setError('Connection error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatUptime = (seconds) => {
    if (!seconds) return '0m';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  };

  const formatCurrency = (amount) => {
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

          {/* Auto-refresh Toggle */}
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`p-2 rounded-lg transition ${
              autoRefresh ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600'
            }`}
            title="Auto-refresh"
          >
            <RefreshCw className={`w-5 h-5 ${autoRefresh && status === 'running' ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="bg-red-50 border-2 border-red-500 rounded-lg p-4 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-red-900">Error</p>
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
              'No trades yet'
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
              className="flex-1 bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition font-medium disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  Start Bot
                </>
              )}
            </button>
          )}

          {/* Pause Button */}
          {status === 'running' && (
            <button
              onClick={() => handleAction('pause')}
              disabled={loading}
              className="flex-1 bg-yellow-600 text-white px-6 py-3 rounded-lg hover:bg-yellow-700 transition font-medium disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              ) : (
                <>
                  <Pause className="w-5 h-5" />
                  Pause Bot
                </>
              )}
            </button>
          )}

          {/* Stop Button */}
          {(status === 'running' || status === 'paused') && (
            <button
              onClick={() => handleAction('stop')}
              disabled={loading}
              className="flex-1 bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700 transition font-medium disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              ) : (
                <>
                  <Square className="w-5 h-5" />
                  Stop Bot
                </>
              )}
            </button>
          )}

          {/* Refresh Button */}
          <button
            onClick={fetchBotStatus}
            disabled={loading}
            className="px-6 py-3 border-2 border-gray-300 rounded-lg hover:bg-gray-50 transition disabled:opacity-50"
            title="Refresh status"
          >
            <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {/* Status Messages */}
        {status === 'stopped' && (
          <div className="mt-4 p-3 bg-gray-50 rounded-lg text-sm text-gray-600">
            💡 Bot is currently stopped. Click "Start Bot" to begin trading.
          </div>
        )}
        {status === 'paused' && (
          <div className="mt-4 p-3 bg-yellow-50 rounded-lg text-sm text-yellow-700">
            ⏸️ Bot is paused. No new trades will be opened. Click "Start Bot" to resume.
          </div>
        )}
        {status === 'running' && (
          <div className="mt-4 p-3 bg-green-50 rounded-lg text-sm text-green-700">
            ✅ Bot is actively trading. Monitoring markets for opportunities...
          </div>
        )}
      </div>

      {/* Confirmation Modal */}
      {showConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <div className="flex items-center gap-3 mb-4">
              <AlertTriangle className="w-8 h-8 text-red-600" />
              <h3 className="text-xl font-bold">Confirm Stop Bot</h3>
            </div>
            
            <p className="text-gray-600 mb-6">
              Are you sure you want to stop this bot? All open positions will be closed at market price.
            </p>

            <div className="flex gap-3">
              <button
                onClick={() => executeAction(confirmAction)}
                disabled={loading}
                className="flex-1 bg-red-600 text-white px-4 py-2.5 rounded-lg hover:bg-red-700 transition font-medium disabled:opacity-50"
              >
                {loading ? 'Stopping...' : 'Yes, Stop Bot'}
              </button>
              <button
                onClick={() => {
                  setShowConfirm(false);
                  setConfirmAction(null);
                }}
                disabled={loading}
                className="flex-1 border-2 border-gray-300 px-4 py-2.5 rounded-lg hover:bg-gray-50 transition disabled:opacity-50"
              >
                Cancel
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
            <li>• Pause: Stops opening new trades, keeps existing positions</li>
            <li>• Stop: Closes all positions and stops the bot</li>
            <li>• Emergency stop available 24/7 via mobile app</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default BotControls;
