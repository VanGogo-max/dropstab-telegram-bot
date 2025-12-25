import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Activity, DollarSign, Bot, Gift, AlertCircle } from 'lucide-react';

const Dashboard = () => {
  const [portfolio, setPortfolio] = useState({ value: 0, change: 0 });
  const [activeBots, setActiveBots] = useState([]);
  const [subscription, setSubscription] = useState({ daysLeft: 0, price: 10 });
  const [referrals, setReferrals] = useState({ count: 0, discount: 0 });
  const [recentTrades, setRecentTrades] = useState([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch('/api/dashboard', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await response.json();
      setPortfolio(data.portfolio);
      setActiveBots(data.active_bots);
      setSubscription(data.subscription);
      setReferrals(data.referrals);
      setRecentTrades(data.recent_trades);
    } catch (error) {
      console.error('Dashboard fetch error:', error);
    }
  };

  const botStatusColor = (status: string) => {
    return status === 'active' ? 'bg-green-500' : status === 'idle' ? 'bg-yellow-500' : 'bg-gray-500';
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Welcome back! Here's your trading overview.</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Portfolio Value */}
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 bg-blue-100 rounded-lg">
                <DollarSign className="w-6 h-6 text-blue-600" />
              </div>
              {portfolio.change >= 0 ? (
                <TrendingUp className="w-5 h-5 text-green-500" />
              ) : (
                <TrendingDown className="w-5 h-5 text-red-500" />
              )}
            </div>
            <h3 className="text-sm font-medium text-gray-600 mb-1">Portfolio Value</h3>
            <p className="text-2xl font-bold text-gray-900">${portfolio.value.toLocaleString()}</p>
            <p className={`text-sm mt-1 ${portfolio.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {portfolio.change >= 0 ? '+' : ''}{portfolio.change.toFixed(2)}% (24h)
            </p>
          </div>

          {/* Active Bots */}
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 bg-green-100 rounded-lg">
                <Bot className="w-6 h-6 text-green-600" />
              </div>
              <Activity className="w-5 h-5 text-gray-400" />
            </div>
            <h3 className="text-sm font-medium text-gray-600 mb-1">Active Bots</h3>
            <p className="text-2xl font-bold text-gray-900">{activeBots.length}/10</p>
            <p className="text-sm text-gray-500 mt-1">{10 - activeBots.length} available</p>
          </div>

          {/* Subscription */}
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 bg-purple-100 rounded-lg">
                <AlertCircle className="w-6 h-6 text-purple-600" />
              </div>
            </div>
            <h3 className="text-sm font-medium text-gray-600 mb-1">Subscription</h3>
            <p className="text-2xl font-bold text-gray-900">${subscription.price}/mo</p>
            <p className="text-sm text-gray-500 mt-1">{subscription.daysLeft} days remaining</p>
          </div>

          {/* Referrals */}
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 bg-orange-100 rounded-lg">
                <Gift className="w-6 h-6 text-orange-600" />
              </div>
            </div>
            <h3 className="text-sm font-medium text-gray-600 mb-1">Referral Savings</h3>
            <p className="text-2xl font-bold text-gray-900">${referrals.discount}/mo</p>
            <p className="text-sm text-gray-500 mt-1">{referrals.count} referrals active</p>
          </div>
        </div>

        {/* Active Bots Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2 bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">Active Bots</h2>
              <button 
                onClick={() => window.location.href = '/bots'}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                Add New Bot →
              </button>
            </div>

            {activeBots.length === 0 ? (
              <div className="text-center py-12">
                <Bot className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-600 mb-4">No active bots yet</p>
                <button 
                  onClick={() => window.location.href = '/bots'}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Start Your First Bot
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                {activeBots.map((bot: any, idx: number) => (
                  <div key={idx} className="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`w-2 h-2 rounded-full ${botStatusColor(bot.status)}`}></div>
                        <div>
                          <h3 className="font-medium text-gray-900">{bot.name}</h3>
                          <p className="text-sm text-gray-600">{bot.exchange}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className={`font-semibold ${bot.profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {bot.profit >= 0 ? '+' : ''}${bot.profit.toFixed(2)}
                        </p>
                        <p className="text-sm text-gray-500">{bot.duration}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Recent Trades */}
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <h2 className="text-xl font-bold text-gray-900 mb-6">Recent Trades</h2>
            <div className="space-y-4">
              {recentTrades.length === 0 ? (
                <p className="text-gray-500 text-sm text-center py-8">No trades yet</p>
              ) : (
                recentTrades.slice(0, 5).map((trade: any, idx: number) => (
                  <div key={idx} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{trade.symbol}</p>
                      <p className="text-xs text-gray-500">{trade.time}</p>
                    </div>
                    <div className="text-right">
                      <span className={`text-xs px-2 py-1 rounded ${
                        trade.side === 'BUY' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                      }`}>
                        {trade.side}
                      </span>
                      <p className="text-sm font-medium text-gray-900 mt-1">${trade.price.toLocaleString()}</p>
                    </div>
                  </div>
                ))
              )}
            </div>
            {recentTrades.length > 5 && (
              <button 
                onClick={() => window.location.href = '/trades'}
                className="w-full mt-4 text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                View All Trades →
              </button>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl shadow-lg p-8 text-white">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h3 className="text-lg font-semibold mb-2">Add Your First Bot</h3>
              <p className="text-blue-100 text-sm mb-4">Start automated trading in minutes</p>
              <button 
                onClick={() => window.location.href = '/bots'}
                className="px-6 py-2 bg-white text-blue-600 rounded-lg hover:bg-blue-50 font-medium"
              >
                Browse Bots
              </button>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-2">Connect Exchange</h3>
              <p className="text-blue-100 text-sm mb-4">Link your KCEX or Hyperliquid account</p>
              <button 
                onClick={() => window.location.href = '/settings/api-keys'}
                className="px-6 py-2 bg-white/20 text-white rounded-lg hover:bg-white/30 font-medium backdrop-blur"
              >
                Connect Now
              </button>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-2">Earn Free Subscription</h3>
              <p className="text-blue-100 text-sm mb-4">Invite friends and save ${referrals.count}/10</p>
              <button 
                onClick={() => window.location.href = '/referrals'}
                className="px-6 py-2 bg-white/20 text-white rounded-lg hover:bg-white/30 font-medium backdrop-blur"
              >
                Share Code
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
