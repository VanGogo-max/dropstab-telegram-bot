// AnalyticsDashboard.tsx - Advanced Analytics & Charts
import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import './AnalyticsDashboard.css';

// Types
interface PerformanceData {
  date: string;
  profit: number;
  trades: number;
  winRate: number;
}

interface BotPerformance {
  botType: string;
  profit: number;
  trades: number;
  winRate: number;
}

interface TradeData {
  id: string;
  symbol: string;
  side: string;
  profit: number;
  date: string;
  bot: string;
}

function AnalyticsDashboard() {
  const [timeRange, setTimeRange] = useState('7d');
  const [performanceData, setPerformanceData] = useState<PerformanceData[]>([]);
  const [botPerformance, setBotPerformance] = useState<BotPerformance[]>([]);
  const [recentTrades, setRecentTrades] = useState<TradeData[]>([]);

  useEffect(() => {
    fetchAnalytics();
  }, [timeRange]);

  const fetchAnalytics = async () => {
    // Mock data - replace with API call
    setPerformanceData(generateMockPerformanceData());
    setBotPerformance(generateMockBotData());
    setRecentTrades(generateMockTrades());
  };

  const generateMockPerformanceData = (): PerformanceData[] => {
    const data = [];
    const days = timeRange === '7d' ? 7 : timeRange === '30d' ? 30 : 90;
    
    for (let i = days; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      
      data.push({
        date: date.toISOString().split('T')[0],
        profit: Math.random() * 200 - 50,
        trades: Math.floor(Math.random() * 20) + 5,
        winRate: Math.random() * 0.4 + 0.5
      });
    }
    return data;
  };

  const generateMockBotData = (): BotPerformance[] => {
    return [
      { botType: 'DCA', profit: 450, trades: 120, winRate: 0.78 },
      { botType: 'Signal', profit: 320, trades: 85, winRate: 0.65 },
      { botType: 'Portfolio', profit: 280, trades: 45, winRate: 0.72 },
      { botType: 'Trailing', profit: 190, trades: 38, winRate: 0.81 },
      { botType: 'Arbitrage', profit: 150, trades: 52, winRate: 0.88 }
    ];
  };

  const generateMockTrades = (): TradeData[] => {
    const symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT'];
    const bots = ['DCA', 'Signal', 'Trailing'];
    const trades = [];
    
    for (let i = 0; i < 10; i++) {
      trades.push({
        id: `trade_${i}`,
        symbol: symbols[Math.floor(Math.random() * symbols.length)],
        side: Math.random() > 0.5 ? 'buy' : 'sell',
        profit: Math.random() * 100 - 20,
        date: new Date().toISOString(),
        bot: bots[Math.floor(Math.random() * bots.length)]
      });
    }
    return trades;
  };

  const totalProfit = performanceData.reduce((sum, d) => sum + d.profit, 0);
  const totalTrades = performanceData.reduce((sum, d) => sum + d.trades, 0);
  const avgWinRate = performanceData.reduce((sum, d) => sum + d.winRate, 0) / performanceData.length;

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

  return (
    <div className="analytics-dashboard">
      <div className="analytics-header">
        <h1>📊 Advanced Analytics</h1>
        
        <div className="time-range-selector">
          <button 
            className={timeRange === '7d' ? 'active' : ''}
            onClick={() => setTimeRange('7d')}
          >
            7 Days
          </button>
          <button 
            className={timeRange === '30d' ? 'active' : ''}
            onClick={() => setTimeRange('30d')}
          >
            30 Days
          </button>
          <button 
            className={timeRange === '90d' ? 'active' : ''}
            onClick={() => setTimeRange('90d')}
          >
            90 Days
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="summary-cards">
        <SummaryCard 
          title="Total Profit" 
          value={`$${totalProfit.toFixed(2)}`}
          change="+12.5%"
          positive={totalProfit >= 0}
        />
        <SummaryCard 
          title="Total Trades" 
          value={totalTrades}
          change="+8 today"
        />
        <SummaryCard 
          title="Avg Win Rate" 
          value={`${(avgWinRate * 100).toFixed(1)}%`}
          change="+2.3%"
          positive={true}
        />
        <SummaryCard 
          title="Active Bots" 
          value="5"
          change="All operational"
        />
      </div>

      {/* Profit Chart */}
      <div className="chart-card">
        <h2>Profit Over Time</h2>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={performanceData}>
            <defs>
              <linearGradient id="colorProfit" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3a" />
            <XAxis dataKey="date" stroke="#9ca3af" />
            <YAxis stroke="#9ca3af" />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#12121a', 
                border: '1px solid #2a2a3a',
                borderRadius: '8px'
              }}
            />
            <Area 
              type="monotone" 
              dataKey="profit" 
              stroke="#10b981" 
              fillOpacity={1} 
              fill="url(#colorProfit)" 
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="charts-grid">
        {/* Trades Chart */}
        <div className="chart-card">
          <h2>Daily Trades</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3a" />
              <XAxis dataKey="date" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#12121a', 
                  border: '1px solid #2a2a3a',
                  borderRadius: '8px'
                }}
              />
              <Bar dataKey="trades" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Win Rate Chart */}
        <div className="chart-card">
          <h2>Win Rate Trend</h2>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3a" />
              <XAxis dataKey="date" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#12121a', 
                  border: '1px solid #2a2a3a',
                  borderRadius: '8px'
                }}
              />
              <Line 
                type="monotone" 
                dataKey="winRate" 
                stroke="#10b981" 
                strokeWidth={2}
                dot={{ fill: '#10b981' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Bot Performance */}
      <div className="charts-grid">
        <div className="chart-card">
          <h2>Bot Performance Comparison</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={botPerformance} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3a" />
              <XAxis type="number" stroke="#9ca3af" />
              <YAxis dataKey="botType" type="category" stroke="#9ca3af" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#12121a', 
                  border: '1px solid #2a2a3a',
                  borderRadius: '8px'
                }}
              />
              <Bar dataKey="profit" fill="#10b981" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h2>Profit Distribution</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={botPerformance}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ botType, profit }) => `${botType}: $${profit}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="profit"
              >
                {botPerformance.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Bot Stats Table */}
      <div className="stats-table-card">
        <h2>Bot Statistics</h2>
        <table className="stats-table">
          <thead>
            <tr>
              <th>Bot Type</th>
              <th>Total Profit</th>
              <th>Trades</th>
              <th>Win Rate</th>
              <th>Avg Profit/Trade</th>
            </tr>
          </thead>
          <tbody>
            {botPerformance.map((bot, index) => (
              <tr key={index}>
                <td>
                  <span className="bot-badge" style={{ background: COLORS[index] }}>
                    {bot.botType}
                  </span>
                </td>
                <td className={bot.profit >= 0 ? 'positive' : 'negative'}>
                  ${bot.profit.toFixed(2)}
                </td>
                <td>{bot.trades}</td>
                <td>{(bot.winRate * 100).toFixed(1)}%</td>
                <td>${(bot.profit / bot.trades).toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Recent Trades */}
      <div className="recent-trades-card">
        <h2>Recent Trades</h2>
        <div className="trades-list">
          {recentTrades.map((trade) => (
            <div key={trade.id} className="trade-item">
              <div className="trade-info">
                <span className="trade-symbol">{trade.symbol}</span>
                <span className="trade-bot">{trade.bot}</span>
              </div>
              <div className="trade-details">
                <span className={`trade-side ${trade.side}`}>{trade.side.toUpperCase()}</span>
                <span className={`trade-profit ${trade.profit >= 0 ? 'positive' : 'negative'}`}>
                  {trade.profit >= 0 ? '+' : ''}${trade.profit.toFixed(2)}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Summary Card Component
const SummaryCard: React.FC<{
  title: string;
  value: string | number;
  change?: string;
  positive?: boolean;
}> = ({ title, value, change, positive }) => {
  return (
    <div className="summary-card">
      <h3>{title}</h3>
      <div className="summary-value">{value}</div>
      {change && (
        <div className={`summary-change ${positive ? 'positive' : ''}`}>
          {change}
        </div>
      )}
    </div>
  );
};

export default AnalyticsDashboard;
