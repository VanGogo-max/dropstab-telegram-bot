// AdminDashboard.tsx - Admin Control Panel
import React, { useState, useEffect } from 'react';
import './AdminDashboard.css';

interface User {
  id: string;
  username: string;
  email: string;
  subscription_status: string;
  created_at: string;
  last_login: string;
}

interface SystemStats {
  totalUsers: number;
  activeUsers: number;
  totalBots: number;
  activeBots: number;
  totalRevenue: number;
  monthlyRevenue: number;
}

interface BotStats {
  dca: number;
  signal: number;
  portfolio: number;
  trailing: number;
  arbitrage: number;
}

function AdminDashboard() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  
  const [users, setUsers] = useState<User[]>([]);
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null);
  const [botStats, setBotStats] = useState<BotStats | null>(null);
  const [logs, setLogs] = useState<string[]>([]);

  const handleLogin = () => {
    // Simple password check
    if (password === 'admin123') { // TODO: Use environment variable
      setIsAuthenticated(true);
      fetchAdminData();
    } else {
      alert('Invalid password');
    }
  };

  const fetchAdminData = async () => {
    // Fetch all admin data
    await Promise.all([
      fetchSystemStats(),
      fetchUsers(),
      fetchBotStats(),
      fetchLogs()
    ]);
  };

  const fetchSystemStats = async () => {
    try {
      const response = await fetch('/api/admin/stats', {
        headers: { 'X-Admin-Password': password }
      });
      const data = await response.json();
      setSystemStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await fetch('/api/admin/users', {
        headers: { 'X-Admin-Password': password }
      });
      const data = await response.json();
      setUsers(data.users);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const fetchBotStats = async () => {
    // Mock data for now
    setBotStats({
      dca: 45,
      signal: 32,
      portfolio: 28,
      trailing: 21,
      arbitrage: 15
    });
  };

  const fetchLogs = async () => {
    // Mock logs
    setLogs([
      '[2024-01-15 10:30:45] User user123 started DCA bot',
      '[2024-01-15 10:28:12] New payment verified: $39.00',
      '[2024-01-15 10:25:33] User user456 logged in',
      '[2024-01-15 10:20:15] System backup completed',
      '[2024-01-15 10:15:00] Risk manager: Emergency stop triggered for user789'
    ]);
  };

  if (!isAuthenticated) {
    return (
      <div className="admin-login">
        <div className="admin-login-card">
          <h1>🔐 Admin Panel</h1>
          <input
            type="password"
            placeholder="Admin Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
          />
          <button onClick={handleLogin}>Login</button>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      <aside className="admin-sidebar">
        <h2>⚡ Admin</h2>
        <nav>
          <button 
            className={activeTab === 'overview' ? 'active' : ''}
            onClick={() => setActiveTab('overview')}
          >
            📊 Overview
          </button>
          <button 
            className={activeTab === 'users' ? 'active' : ''}
            onClick={() => setActiveTab('users')}
          >
            👥 Users
          </button>
          <button 
            className={activeTab === 'bots' ? 'active' : ''}
            onClick={() => setActiveTab('bots')}
          >
            🤖 Bots
          </button>
          <button 
            className={activeTab === 'payments' ? 'active' : ''}
            onClick={() => setActiveTab('payments')}
          >
            💳 Payments
          </button>
          <button 
            className={activeTab === 'logs' ? 'active' : ''}
            onClick={() => setActiveTab('logs')}
          >
            📝 Logs
          </button>
          <button 
            className={activeTab === 'settings' ? 'active' : ''}
            onClick={() => setActiveTab('settings')}
          >
            ⚙️ Settings
          </button>
        </nav>
      </aside>

      <main className="admin-content">
        {activeTab === 'overview' && (
          <OverviewTab stats={systemStats} botStats={botStats} />
        )}
        
        {activeTab === 'users' && (
          <UsersTab users={users} onRefresh={fetchUsers} />
        )}
        
        {activeTab === 'bots' && (
          <BotsTab botStats={botStats} />
        )}
        
        {activeTab === 'payments' && (
          <PaymentsTab />
        )}
        
        {activeTab === 'logs' && (
          <LogsTab logs={logs} />
        )}
        
        {activeTab === 'settings' && (
          <SettingsTab />
        )}
      </main>
    </div>
  );
}

// Overview Tab
const OverviewTab: React.FC<{ 
  stats: SystemStats | null; 
  botStats: BotStats | null;
}> = ({ stats, botStats }) => {
  return (
    <div className="overview-tab">
      <h1>System Overview</h1>
      
      <div className="stats-grid">
        <StatCard title="Total Users" value={stats?.totalUsers || 0} icon="👥" />
        <StatCard title="Active Users" value={stats?.activeUsers || 0} icon="🟢" />
        <StatCard title="Total Bots" value={stats?.totalBots || 0} icon="🤖" />
        <StatCard title="Active Bots" value={stats?.activeBots || 0} icon="⚡" />
        <StatCard 
          title="Total Revenue" 
          value={`$${stats?.totalRevenue.toFixed(2) || '0.00'}`} 
          icon="💰" 
        />
        <StatCard 
          title="Monthly Revenue" 
          value={`$${stats?.monthlyRevenue.toFixed(2) || '0.00'}`} 
          icon="📈" 
        />
      </div>

      <div className="charts-section">
        <div className="chart-card">
          <h3>Bot Distribution</h3>
          {botStats && (
            <div className="bot-distribution">
              {Object.entries(botStats).map(([bot, count]) => (
                <div key={bot} className="bot-bar">
                  <span className="bot-name">{bot.toUpperCase()}</span>
                  <div className="bar-container">
                    <div 
                      className="bar-fill" 
                      style={{ width: `${(count / 141) * 100}%` }}
                    />
                    <span className="bar-value">{count}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Users Tab
const UsersTab: React.FC<{ users: User[]; onRefresh: () => void }> = ({ users, onRefresh }) => {
  const [searchTerm, setSearchTerm] = useState('');
  
  const filteredUsers = users.filter(user => 
    user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="users-tab">
      <div className="tab-header">
        <h1>Users Management</h1>
        <button onClick={onRefresh} className="refresh-btn">🔄 Refresh</button>
      </div>
      
      <input
        type="text"
        placeholder="Search users..."
        className="search-input"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />
      
      <table className="users-table">
        <thead>
          <tr>
            <th>Username</th>
            <th>Email</th>
            <th>Status</th>
            <th>Created</th>
            <th>Last Login</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {filteredUsers.map(user => (
            <tr key={user.id}>
              <td>{user.username}</td>
              <td>{user.email}</td>
              <td>
                <span className={`status-badge ${user.subscription_status}`}>
                  {user.subscription_status}
                </span>
              </td>
              <td>{new Date(user.created_at).toLocaleDateString()}</td>
              <td>{new Date(user.last_login).toLocaleDateString()}</td>
              <td>
                <button className="action-btn view">View</button>
                <button className="action-btn edit">Edit</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// Bots Tab
const BotsTab: React.FC<{ botStats: BotStats | null }> = ({ botStats }) => {
  return (
    <div className="bots-tab">
      <h1>Bot Statistics</h1>
      
      <div className="bot-stats-grid">
        {botStats && Object.entries(botStats).map(([bot, count]) => (
          <div key={bot} className="bot-stat-card">
            <h3>{bot.toUpperCase()} Bot</h3>
            <div className="bot-stat-value">{count}</div>
            <div className="bot-stat-label">Active Instances</div>
          </div>
        ))}
      </div>
      
      <div className="bot-actions">
        <h2>System Actions</h2>
        <button className="action-btn danger">🛑 Emergency Stop All Bots</button>
        <button className="action-btn warning">⚠️ Pause All Trading</button>
        <button className="action-btn success">✅ Resume All Trading</button>
      </div>
    </div>
  );
};

// Payments Tab
const PaymentsTab: React.FC = () => {
  const payments = [
    { id: 1, user: 'user123', amount: 39.00, status: 'verified', date: '2024-01-15' },
    { id: 2, user: 'user456', amount: 31.20, status: 'verified', date: '2024-01-14' },
    { id: 3, user: 'user789', amount: 19.50, status: 'pending', date: '2024-01-14' },
  ];

  return (
    <div className="payments-tab">
      <h1>Payment History</h1>
      
      <div className="payment-summary">
        <div className="summary-card">
          <h3>Today's Revenue</h3>
          <p className="summary-value">$195.00</p>
        </div>
        <div className="summary-card">
          <h3>This Month</h3>
          <p className="summary-value">$2,340.00</p>
        </div>
        <div className="summary-card">
          <h3>Pending</h3>
          <p className="summary-value">$58.50</p>
        </div>
      </div>
      
      <table className="payments-table">
        <thead>
          <tr>
            <th>User</th>
            <th>Amount</th>
            <th>Status</th>
            <th>Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {payments.map(payment => (
            <tr key={payment.id}>
              <td>{payment.user}</td>
              <td>${payment.amount.toFixed(2)}</td>
              <td>
                <span className={`status-badge ${payment.status}`}>
                  {payment.status}
                </span>
              </td>
              <td>{payment.date}</td>
              <td>
                <button className="action-btn view">View TX</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// Logs Tab
const LogsTab: React.FC<{ logs: string[] }> = ({ logs }) => {
  return (
    <div className="logs-tab">
      <h1>System Logs</h1>
      
      <div className="logs-container">
        {logs.map((log, index) => (
          <div key={index} className="log-entry">
            {log}
          </div>
        ))}
      </div>
      
      <button className="action-btn">📥 Download Full Logs</button>
    </div>
  );
};

// Settings Tab
const SettingsTab: React.FC = () => {
  return (
    <div className="settings-tab">
      <h1>System Settings</h1>
      
      <div className="settings-section">
        <h3>General Settings</h3>
        <label>
          <input type="checkbox" defaultChecked />
          Enable new user registrations
        </label>
        <label>
          <input type="checkbox" defaultChecked />
          Allow testnet trading
        </label>
        <label>
          <input type="checkbox" />
          Maintenance mode
        </label>
      </div>
      
      <div className="settings-section">
        <h3>Risk Management</h3>
        <label>
          Max daily loss limit:
          <input type="number" defaultValue="5" /> %
        </label>
        <label>
          Max drawdown:
          <input type="number" defaultValue="10" /> %
        </label>
      </div>
      
      <button className="action-btn success">💾 Save Settings</button>
    </div>
  );
};

// Stat Card Component
const StatCard: React.FC<{ title: string; value: number | string; icon: string }> = 
  ({ title, value, icon }) => {
  
  return (
    <div className="admin-stat-card">
      <span className="stat-icon">{icon}</span>
      <div>
        <h3>{title}</h3>
        <p className="stat-value">{value}</p>
      </div>
    </div>
  );
};

export default AdminDashboard;
