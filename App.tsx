// App.tsx - Main React Application
import React, { useState, useEffect } from 'react';
import './App.css';

// Types
interface Bot {
  id: string;
  type: string;
  status: string;
  config: any;
}

interface Performance {
  totalProfit: number;
  totalTrades: number;
  activeBots: number;
  winRate: number;
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [bots, setBots] = useState<Bot[]>([]);
  const [performance, setPerformance] = useState<Performance | null>(null);
  const [activeTab, setActiveTab] = useState('dashboard');

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('token');
    if (token) {
      setIsAuthenticated(true);
      fetchBots();
      fetchPerformance();
    }
  }, []);

  const fetchBots = async () => {
    try {
      const response = await fetch('/api/bots/status', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setBots(Object.values(data.bots));
    } catch (error) {
      console.error('Error fetching bots:', error);
    }
  };

  const fetchPerformance = async () => {
    try {
      const response = await fetch('/api/performance', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setPerformance(data);
    } catch (error) {
      console.error('Error fetching performance:', error);
    }
  };

  const startBot = async (botType: string, config: any) => {
    try {
      const response = await fetch(`/api/bots/${botType}/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(config)
      });
      const data = await response.json();
      if (data.success) {
        fetchBots();
      }
    } catch (error) {
      console.error('Error starting bot:', error);
    }
  };

  const stopBot = async (botId: string) => {
    try {
      const response = await fetch(`/api/bots/${botId}/stop`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        fetchBots();
      }
    } catch (error) {
      console.error('Error stopping bot:', error);
    }
  };

  if (!isAuthenticated) {
    return <LoginScreen onLogin={() => setIsAuthenticated(true)} />;
  }

  return (
    <div className="app">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <main className="main-content">
        {activeTab === 'dashboard' && (
          <Dashboard performance={performance} bots={bots} />
        )}
        
        {activeTab === 'bots' && (
          <BotsManager 
            bots={bots} 
            onStart={startBot} 
            onStop={stopBot} 
          />
        )}
        
        {activeTab === 'performance' && (
          <PerformanceView performance={performance} />
        )}
        
        {activeTab === 'subscription' && (
          <SubscriptionView />
        )}
        
        {activeTab === 'referral' && (
          <ReferralView />
        )}
      </main>
    </div>
  );
}

// Login Screen
const LoginScreen: React.FC<{ onLogin: () => void }> = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/user/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await response.json();
      if (data.token) {
        localStorage.setItem('token', data.token);
        onLogin();
      }
    } catch (error) {
      console.error('Login error:', error);
    }
  };

  return (
    <div className="login-screen">
      <div className="login-card">
        <h1>🚀 CryptoTradeBot Pro</h1>
        <form onSubmit={handleLogin}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button type="submit">Login</button>
        </form>
      </div>
    </div>
  );
};

// Sidebar Navigation
const Sidebar: React.FC<{ activeTab: string; setActiveTab: (tab: string) => void }> = 
  ({ activeTab, setActiveTab }) => {
  
  const tabs = [
    { id: 'dashboard', icon: '📊', label: 'Dashboard' },
    { id: 'bots', icon: '🤖', label: 'Bots' },
    { id: 'performance', icon: '📈', label: 'Performance' },
    { id: 'subscription', icon: '💳', label: 'Subscription' },
    { id: 'referral', icon: '🎁', label: 'Referral' }
  ];

  return (
    <aside className="sidebar">
      <div className="logo">💼 CryptoBot</div>
      <nav>
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={activeTab === tab.id ? 'active' : ''}
            onClick={() => setActiveTab(tab.id)}
          >
            <span className="icon">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </nav>
    </aside>
  );
};

// Dashboard
const Dashboard: React.FC<{ performance: Performance | null; bots: Bot[] }> = 
  ({ performance, bots }) => {
  
  return (
    <div className="dashboard">
      <h1>Dashboard</h1>
      
      <div className="stats-grid">
        <StatCard 
          title="Total P&L" 
          value={`$${performance?.totalProfit.toFixed(2) || '0.00'}`}
          trend="+12.5%"
        />
        <StatCard 
          title="Active Bots" 
          value={performance?.activeBots || 0}
        />
        <StatCard 
          title="Total Trades" 
          value={performance?.totalTrades || 0}
        />
        <StatCard 
          title="Win Rate" 
          value={`${((performance?.winRate || 0) * 100).toFixed(1)}%`}
        />
      </div>
      
      <div className="bots-overview">
        <h2>Active Bots</h2>
        {bots.length > 0 ? (
          bots.map(bot => (
            <BotCard key={bot.id} bot={bot} />
          ))
        ) : (
          <p>No active bots. Start your first bot!</p>
        )}
      </div>
    </div>
  );
};

// Stat Card Component
const StatCard: React.FC<{ title: string; value: string | number; trend?: string }> = 
  ({ title, value, trend }) => {
  
  return (
    <div className="stat-card">
      <h3>{title}</h3>
      <div className="value">{value}</div>
      {trend && <div className="trend">{trend}</div>}
    </div>
  );
};

// Bot Card Component
const BotCard: React.FC<{ bot: Bot }> = ({ bot }) => {
  const statusColor = bot.status === 'running' ? '#00ff00' : '#ff0000';
  
  return (
    <div className="bot-card">
      <div className="bot-header">
        <h3>{bot.type.toUpperCase()} Bot</h3>
        <span className="status" style={{ color: statusColor }}>
          ● {bot.status}
        </span>
      </div>
      <div className="bot-details">
        <p>ID: {bot.id}</p>
      </div>
    </div>
  );
};

// Bots Manager
const BotsManager: React.FC<{
  bots: Bot[];
  onStart: (type: string, config: any) => void;
  onStop: (id: string) => void;
}> = ({ bots, onStart, onStop }) => {
  
  const botTypes = [
    { id: 'dca', name: 'DCA Bot', icon: '🔄' },
    { id: 'signal', name: 'Signal Bot', icon: '📊' },
    { id: 'portfolio', name: 'Portfolio Bot', icon: '💼' },
    { id: 'trailing', name: 'Trailing Stop', icon: '🎯' },
    { id: 'arbitrage', name: 'Arbitrage Bot', icon: '⚖️' }
  ];

  return (
    <div className="bots-manager">
      <h1>Bots Manager</h1>
      
      <div className="bot-types-grid">
        {botTypes.map(type => (
          <div key={type.id} className="bot-type-card">
            <div className="icon">{type.icon}</div>
            <h3>{type.name}</h3>
            <button onClick={() => onStart(type.id, {})}>
              Start Bot
            </button>
          </div>
        ))}
      </div>
      
      <div className="active-bots-list">
        <h2>Active Bots</h2>
        {bots.map(bot => (
          <div key={bot.id} className="bot-list-item">
            <span>{bot.type}</span>
            <span className="status">{bot.status}</span>
            <button onClick={() => onStop(bot.id)}>Stop</button>
          </div>
        ))}
      </div>
    </div>
  );
};

// Performance View
const PerformanceView: React.FC<{ performance: Performance | null }> = ({ performance }) => {
  return (
    <div className="performance-view">
      <h1>Performance Analytics</h1>
      {/* Add charts and detailed analytics here */}
      <p>Total Profit: ${performance?.totalProfit.toFixed(2)}</p>
    </div>
  );
};

// Subscription View
const SubscriptionView: React.FC = () => {
  return (
    <div className="subscription-view">
      <h1>Subscription</h1>
      <div className="pricing-card">
        <h2>$39/month</h2>
        <p>Full access to all bots</p>
        <button>Subscribe Now</button>
      </div>
    </div>
  );
};

// Referral View
const ReferralView: React.FC = () => {
  return (
    <div className="referral-view">
      <h1>Referral Program</h1>
      <p>Share your referral link and get discounts!</p>
    </div>
  );
};

export default App;
