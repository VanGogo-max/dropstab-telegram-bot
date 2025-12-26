import React, { useState } from 'react';
import { TrendingUp, DollarSign, BarChart3, Shield, Grid3x3, Zap, Activity, ArrowLeftRight, Target, Repeat } from 'lucide-react';

const BotSelector = () => {
  const [filter, setFilter] = useState('all');
  const [riskFilter, setRiskFilter] = useState('all');

  const bots = [
    {
      id: 'dca',
      name: 'DCA Bot',
      icon: Repeat,
      description: 'Auto-buy at regular intervals',
      risk: 'low',
      category: 'spot',
      exchange: 'KCEX',
      winRate: 'N/A',
      features: ['Long-term accumulation', 'Set & forget', 'Perfect for beginners'],
      color: 'blue'
    },
    {
      id: 'signal',
      name: 'Signal Bot',
      icon: Activity,
      description: 'Technical analysis (RSI, MACD, BB)',
      risk: 'medium',
      category: 'spot',
      exchange: 'KCEX',
      winRate: '65%',
      features: ['RSI oversold/overbought', 'MACD crossovers', 'Bollinger Bands'],
      color: 'green'
    },
    {
      id: 'portfolio',
      name: 'Portfolio Bot',
      icon: BarChart3,
      description: 'Auto rebalancing',
      risk: 'low',
      category: 'spot',
      exchange: 'KCEX',
      winRate: 'N/A',
      features: ['Maintain target allocation', 'Diversification', 'Weekly rebalance'],
      color: 'purple'
    },
    {
      id: 'trailing',
      name: 'Trailing Stop',
      icon: Shield,
      description: 'Protect your profits',
      risk: 'low',
      category: 'spot',
      exchange: 'KCEX',
      winRate: 'N/A',
      features: ['Follow price up', 'Auto-sell on dip', 'Lock in gains'],
      color: 'yellow'
    },
    {
      id: 'grid',
      name: 'Grid Bot',
      icon: Grid3x3,
      description: 'Buy low, sell high automatically',
      risk: 'medium',
      category: 'spot',
      exchange: 'KCEX',
      winRate: '70%',
      features: ['Perfect for ranging markets', 'Multiple orders', 'Consistent profits'],
      color: 'indigo'
    },
    {
      id: 'futures',
      name: 'Turtle Futures',
      icon: TrendingUp,
      description: 'Classic Turtle Trading with pyramiding',
      risk: 'high',
      category: 'futures',
      exchange: 'Hyperliquid',
      winRate: '60%',
      features: ['Trend following', 'ATR-based sizing', 'Up to 4 units'],
      color: 'red'
    },
    {
      id: 'dex_arbitrage',
      name: 'DEX Arbitrage',
      icon: ArrowLeftRight,
      description: 'Spot-Futures arbitrage (Decentralized)',
      risk: 'low',
      category: 'arbitrage',
      exchange: 'Uniswap + Hyperliquid',
      winRate: '90%',
      features: ['Funding rate income', 'Basis spread trading', '8-15% APY'],
      color: 'cyan'
    },
    {
      id: 'aggressive_scalper',
      name: 'Aggressive Scalper',
      icon: Zap,
      description: '5-minute momentum scalping',
      risk: 'high',
      category: 'futures',
      exchange: 'Hyperliquid',
      winRate: '60%',
      features: ['High frequency', 'Volume confirmation', 'ATR filter'],
      color: 'orange'
    },
    {
      id: 'trend_master',
      name: 'Trend Master',
      icon: TrendingUp,
      description: 'Smart trend following with pullbacks',
      risk: 'medium',
      category: 'spot',
      exchange: 'KCEX',
      winRate: '70%',
      features: ['1:2 risk-reward', 'RSI filter', 'MACD confirmation'],
      color: 'emerald'
    },
    {
      id: 'mean_reversion',
      name: 'Mean Reversion Pro',
      icon: Target,
      description: 'Bollinger Bands strategy',
      risk: 'low',
      category: 'spot',
      exchange: 'KCEX',
      winRate: '65%',
      features: ['ADX filter', 'Low risk', 'Ranging markets'],
      color: 'teal'
    }
  ];

  const filteredBots = bots.filter(bot => {
    const categoryMatch = filter === 'all' || bot.category === filter;
    const riskMatch = riskFilter === 'all' || bot.risk === riskFilter;
    return categoryMatch && riskMatch;
  });

  const getRiskBadge = (risk: string) => {
    const styles = {
      low: 'bg-green-100 text-green-700',
      medium: 'bg-yellow-100 text-yellow-700',
      high: 'bg-red-100 text-red-700'
    };
    return styles[risk as keyof typeof styles] || '';
  };

  const handleSelectBot = (botId: string) => {
    window.location.href = `/bots/configure/${botId}`;
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Choose Your Trading Bot</h1>
          <p className="text-gray-600 mt-2">Select a bot that matches your trading style and risk tolerance</p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-8 border border-gray-100">
          <div className="flex flex-wrap gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
              <div className="flex gap-2">
                {['all', 'spot', 'futures', 'arbitrage'].map(cat => (
                  <button
                    key={cat}
                    onClick={() => setFilter(cat)}
                    className={`px-4 py-2 rounded-lg font-medium transition ${
                      filter === cat
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {cat.charAt(0).toUpperCase() + cat.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Risk Level</label>
              <div className="flex gap-2">
                {['all', 'low', 'medium', 'high'].map(risk => (
                  <button
                    key={risk}
                    onClick={() => setRiskFilter(risk)}
                    className={`px-4 py-2 rounded-lg font-medium transition ${
                      riskFilter === risk
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {risk.charAt(0).toUpperCase() + risk.slice(1)}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Bots Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredBots.map(bot => {
            const Icon = bot.icon;
            return (
              <div
                key={bot.id}
                className="bg-white rounded-xl shadow-sm border border-gray-100 hover:shadow-lg transition-all duration-300 overflow-hidden"
              >
                <div className={`h-2 bg-${bot.color}-500`}></div>
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className={`p-3 bg-${bot.color}-100 rounded-lg`}>
                      <Icon className={`w-6 h-6 text-${bot.color}-600`} />
                    </div>
                    <span className={`text-xs px-3 py-1 rounded-full font-medium ${getRiskBadge(bot.risk)}`}>
                      {bot.risk.toUpperCase()}
                    </span>
                  </div>

                  <h3 className="text-xl font-bold text-gray-900 mb-2">{bot.name}</h3>
                  <p className="text-gray-600 text-sm mb-4">{bot.description}</p>

                  <div className="space-y-2 mb-4">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Exchange:</span>
                      <span className="font-medium text-gray-900">{bot.exchange}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Win Rate:</span>
                      <span className="font-medium text-gray-900">{bot.winRate}</span>
                    </div>
                  </div>

                  <div className="border-t border-gray-100 pt-4 mb-4">
                    <p className="text-xs font-medium text-gray-700 mb-2">Features:</p>
                    <ul className="space-y-1">
                      {bot.features.map((feature, idx) => (
                        <li key={idx} className="text-xs text-gray-600 flex items-start gap-2">
                          <span className="text-green-500 mt-0.5">✓</span>
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <button
                    onClick={() => handleSelectBot(bot.id)}
                    className={`w-full py-3 bg-${bot.color}-600 text-white rounded-lg font-medium hover:bg-${bot.color}-700 transition`}
                  >
                    Configure Bot
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        {filteredBots.length === 0 && (
          <div className="text-center py-16">
            <p className="text-gray-500 text-lg">No bots match your filters</p>
            <button
              onClick={() => { setFilter('all'); setRiskFilter('all'); }}
              className="mt-4 text-blue-600 hover:text-blue-700 font-medium"
            >
              Clear Filters
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default BotSelector;
