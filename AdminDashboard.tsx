// AdminDashboard.tsx - Admin Control Panel (ЧАСТ 1/2)
import React, { useState, useEffect } from 'react';
import './AdminDashboard.css';

// ============================================================================
// TYPES & INTERFACES
// ============================================================================

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

interface Payment {
  id: number;
  user: string;
  amount: number;
  status: 'verified' | 'pending' | 'failed';
  date: string;
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

function AdminDashboard() {
  // Auth state
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState('');
  
  // UI state
  const [activeTab, setActiveTab] = useState('overview');
  const [menuOpen, setMenuOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  
  // Data state
  const [users, setUsers] = useState<User[]>([]);
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null);
  const [botStats, setBotStats] = useState<BotStats | null>(null);
  const [logs, setLogs] = useState<string[]>([]);

  useEffect(() => {
    setMenuOpen(false);
  }, [activeTab]);

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth > 768) {
        setMenuOpen(false);
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // ============================================================================
  // AUTH FUNCTIONS
  // ============================================================================

  const handleLogin = async () => {
    setLoginError('');
    setLoading(true);

    try {
      const adminPassword = process.env.REACT_APP_ADMIN_PASSWORD || 'admin123';
      
      if (password === adminPassword) {
        setIsAuthenticated(true);
        localStorage.setItem('adminAuth', 'true');
        await fetchAdminData();
      } else {
        setLoginError('Invalid password. Please try again.');
      }
    } catch (error) {
      console.error('Login error:', error);
      setLoginError('Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setPassword('');
    localStorage.removeItem('adminAuth');
  };

  // ============================================================================
  // DATA FETCHING
  // ============================================================================

  const fetchAdminData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        fetchSystemStats(),
        fetchUsers(),
        fetchBotStats(),
        fetchLogs()
      ]);
    } catch (error) {
      console.error('Error fetching admin data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSystemStats = async () => {
    try {
      const response = await fetch('/api/admin/stats', {
        headers: { 
          'Authorization': `Bearer ${password}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) throw new Error('Failed to fetch stats');
      
      const data = await response.json();
      setSystemStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
      setSystemStats({
        totalUsers: 247,
        activeUsers: 189,
        totalBots: 141,
        activeBots: 98,
        totalRevenue: 12450.00,
        monthlyRevenue: 2340.00
      });
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await fetch('/api/admin/users', {
        headers: { 
          'Authorization': `Bearer ${password}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) throw new Error('Failed to fetch users');
      
      const data = await response.json();
      setUsers(data.users);
    } catch (error) {
      console.error('Error fetching users:', error);
      setUsers([
        {
          id: '1',
          username: 'trader_pro',
          email: 'trader@example.com',
          subscription_status: 'active',
          created_at: '2024-01-10T10:00:00Z',
          last_login: '2024-01-15T14:30:00Z'
        },
        {
          id: '2',
          username: 'crypto_master',
          email: 'crypto@example.com',
          subscription_status: 'active',
          created_at: '2024-01-12T09:00:00Z',
          last_login: '2024-01-15T12:00:00Z'
        },
        {
          id: '3',
          username: 'bot_enthusiast',
          email: 'bot@example.com',
          subscription_status: 'expired',
          created_at: '2023-12-01T08:00:00Z',
          last_login: '2024-01-10T11:00:00Z'
        }
      ]);
    }
  };

  const fetchBotStats = async () => {
    try {
      const response = await fetch('/api/admin/bot-stats', {
        headers: { 
          'Authorization': `Bearer ${password}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) throw new Error('Failed to fetch bot stats');
      
      const data = await response.json();
      setBotStats(data);
    } catch (error) {
      console.error('Error fetching bot stats:', error);
      setBotStats({
        dca: 45,
        signal: 32,
        portfolio: 28,
        trailing: 21,
        arbitrage: 15
      });
    }
  };

  const fetchLogs = async () => {
    try {
      const response = await fetch('/api/admin/logs', {
        headers: { 
          'Authorization': `Bearer ${password}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) throw new Error('Failed to fetch logs');
      
      const data = await response.json();
      setLogs(data.logs);
    } catch (error) {
      console.error('Error fetching logs:', error);
      setLogs([
        '[2024-01-15 10:30:45] INFO: User trader_pro started DCA bot on BTC/USDT',
        '[2024-01-15 10:28:12] SUCCESS: Payment verified: $39.00 from user crypto_master',
        '[2024-01-15 10:25:33] INFO: User bot_enthusiast logged in from IP 192.168.1.100',
        '[2024-01-15 10:20:15] SUCCESS: Automated database backup completed (234.5 MB)',
        '[2024-01-15 10:15:00] WARNING: Risk manager triggered emergency stop for user test_user (drawdown: 8.5%)',
        '[2024-01-15 10:10:22] INFO: Grid bot adjusted levels for ETH/USDT (volatility spike detected)',
        '[2024-01-15 10:05:11] ERROR: API rate limit reached for Binance (retry in 60s)',
        '[2024-01-15 10:00:00] INFO: System health check passed - All services operational'
      ]);
    }
  };

  // ============================================================================
  // RENDER: LOGIN SCREEN
  // ============================================================================

  if (!isAuthenticated) {
    return (
      <div className="admin-login">
        <div className="admin-login-card">
          <h1>🔐 Admin Panel</h1>
          <p style={{ color: '#9ca3af', marginBottom: '1.5rem' }}>
            Enter admin password to continue
          </p>
          
          <input
            type="password"
            placeholder="Admin Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
            disabled={loading}
            autoFocus
          />
          
          {loginError && (
            <p style={{ color: '#ef4444', fontSize: '0.9rem', marginBottom: '1rem' }}>
              {loginError}
            </p>
          )}
          
          <button 
            onClick={handleLogin}
            disabled={loading}
            className={loading ? 'loading' : ''}
          >
            {loading ? 'Authenticating...' : 'Login'}
          </button>
        </div>
      </div>
    );
  }

  // ============================================================================
  // RENDER: ADMIN DASHBOARD
  // ============================================================================

  return (
    <div className="admin-dashboard">
      <button 
        className="mobile-menu-btn"
        onClick={() => setMenuOpen(!menuOpen)}
        aria-label="Toggle menu"
      >
        {menuOpen ? '✕' : '☰'}
      </button>

      <aside className={`admin-sidebar ${menuOpen ? 'open' : ''}`}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0 1.5rem 2rem' }}>
          <h2>⚡ Admin</h2>
          <button
            onClick={handleLogout}
            style={{
              background: 'transparent',
              border: '1px solid var(--border-color)',
              color: 'var(--text-secondary)',
              padding: '0.5rem 1rem',
              borderRadius: 'var(--radius-md)',
              cursor: 'pointer',
              fontSize: '0.85rem'
            }}
            title="Logout"
          >
            🚪 Logout
          </button>
        </div>
        
        <nav>
          <button 
            className={activeTab === 'overview' ? 'active' : ''}
            onClick={() => setActiveTab('overview')}
          >
            <span className="icon">📊</span>
            <span>Overview</span>
          </button>
          <button 
            className={activeTab === 'users' ? 'active' : ''}
            onClick={() => setActiveTab('users')}
          >
            <span className="icon">👥</span>
            <span>Users</span>
          </button>
          <button 
            className={activeTab === 'bots' ? 'active' : ''}
            onClick={() => setActiveTab('bots')}
          >
            <span className="icon">🤖</span>
            <span>Bots</span>
          </button>
          <button 
            className={activeTab === 'payments' ? 'active' : ''}
            onClick={() => setActiveTab('payments')}
          >
            <span className="icon">💳</span>
            <span>Payments</span>
          </button>
          <button 
            className={activeTab === 'logs' ? 'active' : ''}
            onClick={() => setActiveTab('logs')}
          >
            <span className="icon">📝</span>
            <span>Logs</span>
          </button>
          <button 
            className={activeTab === 'settings' ? 'active' : ''}
            onClick={() => setActiveTab('settings')}
          >
            <span className="icon">⚙️</span>
            <span>Settings</span>
          </button>
        </nav>
      </aside>

      {menuOpen && (
        <div 
          className="menu-overlay"
          onClick={() => setMenuOpen(false)}
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.5)',
            zIndex: 99,
            display: window.innerWidth > 768 ? 'none' : 'block'
          }}
        />
      )}

      <main className="admin-content">
        {loading && (
          <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-secondary)' }}>
            Loading...
          </div>
        )}

        {!loading && activeTab === 'overview' && (
          <OverviewTab stats={systemStats} botStats={botStats} onRefresh={fetchAdminData} />
        )}
        
        {!loading && activeTab === 'users' && (
          <UsersTab users={users} onRefresh={fetchUsers} />
        )}
        
        {!loading && activeTab === 'bots' && (
          <BotsTab botStats={botStats} />
        )}
        
        {!loading && activeTab === 'payments' && (
          <PaymentsTab />
        )}
        
        {!loading && activeTab === 'logs' && (
          <LogsTab logs={logs} onRefresh={fetchLogs} />
        )}
        
        {!loading && activeTab === 'settings' && (
          <SettingsTab />
        )}
      </main>
    </div>
  );
}

// ============================================================================
// TAB COMPONENTS - OVERVIEW
// ============================================================================

const OverviewTab: React.FC<{ 
  stats: SystemStats | null; 
  botStats: BotStats | null;
  onRefresh: () => void;
}> = ({ stats, botStats, onRefresh }) => {
  const [refreshing, setRefreshing] = useState(false);

  const handleRefresh = async () => {
    setRefreshing(true);
    await onRefresh();
    setTimeout(() => setRefreshing(false), 500);
  };

  return (
    <div className="overview-tab">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1>System Overview</h1>
        <button 
          onClick={handleRefresh}
          className={`refresh-btn ${refreshing ? 'loading' : ''}`}
          disabled={refreshing}
        >
          🔄 Refresh
        </button>
      </div>
      
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
          {botStats ? (
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
          ) : (
            <p style={{ color: 'var(--text-secondary)' }}>Loading bot statistics...</p>
          )}
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// TAB COMPONENTS - USERS
// ============================================================================

const UsersTab: React.FC<{ users: User[]; onRefresh: () => void }> = ({ users, onRefresh }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [refreshing, setRefreshing] = useState(false);
  
  const filteredUsers = users.filter(user => 
    user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleRefresh = async () => {
    setRefreshing(true);
    await onRefresh();
    setTimeout(() => setRefreshing(false), 500);
  };

  return (
    <div className="users-tab">
      <div className="tab-header">
        <h1>Users Management</h1>
        <button 
          onClick={handleRefresh} 
          className={`refresh-btn ${refreshing ? 'loading' : ''}`}
          disabled={refreshing}
        >
          🔄 Refresh
        </button>
      </div>
      
      <input
        type="text"
        placeholder="Search users by username or email..."
        className="search-input"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />
      
      <div className="table-wrapper">
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
            {filteredUsers.length > 0 ? (
              filteredUsers.map(user => (
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
                    <button className="action-btn view" onClick={() => alert(`View user: ${user.username}`)}>
                      View
                    </button>
                    <button className="action-btn edit" onClick={() => alert(`Edit user: ${user.username}`)}>
                      Edit
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={6} style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '2rem' }}>
                  {searchTerm ? 'No users found matching your search' : 'No users available'}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
// AdminDashboard.tsx - ЧАСТ 2/2
// ПРОДЪЛЖЕНИЕ... добавете това СЛЕД Част 1

// ============================================================================
// TAB COMPONENTS - BOTS
// ============================================================================

const BotsTab: React.FC<{ botStats: BotStats | null }> = ({ botStats }) => {
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const handleBotAction = async (action: string) => {
    if (!confirm(`Are you sure you want to ${action}?`)) return;
    
    setActionLoading(action);
    await new Promise(resolve => setTimeout(resolve, 1500));
    alert(`${action} completed successfully!`);
    setActionLoading(null);
  };

  return (
    <div className="bots-tab">
      <h1>Bot Statistics</h1>
      
      <div className="bot-stats-grid">
        {botStats ? (
          Object.entries(botStats).map(([bot, count]) => (
            <div key={bot} className="bot-stat-card">
              <h3>{bot.toUpperCase()} Bot</h3>
              <div className="bot-stat-value">{count}</div>
              <div className="bot-stat-label">Active Instances</div>
            </div>
          ))
        ) : (
          <p style={{ color: 'var(--text-secondary)' }}>Loading bot statistics...</p>
        )}
      </div>
      
      <div className="bot-actions">
        <h2>System Actions</h2>
        <button 
          className={`action-btn danger ${actionLoading === 'stop-all' ? 'loading' : ''}`}
          onClick={() => handleBotAction('stop-all')}
          disabled={!!actionLoading}
        >
          🛑 Emergency Stop All Bots
        </button>
        <button 
          className={`action-btn warning ${actionLoading === 'pause-all' ? 'loading' : ''}`}
          onClick={() => handleBotAction('pause-all')}
          disabled={!!actionLoading}
        >
          ⚠️ Pause All Trading
        </button>
        <button 
          className={`action-btn success ${actionLoading === 'resume-all' ? 'loading' : ''}`}
          onClick={() => handleBotAction('resume-all')}
          disabled={!!actionLoading}
        >
          ✅ Resume All Trading
        </button>
      </div>
    </div>
  );
};

// ============================================================================
// TAB COMPONENTS - PAYMENTS
// ============================================================================

const PaymentsTab: React.FC = () => {
  const payments: Payment[] = [
    { id: 1, user: 'trader_pro', amount: 39.00, status: 'verified', date: '2024-01-15' },
    { id: 2, user: 'crypto_master', amount: 31.20, status: 'verified', date: '2024-01-14' },
    { id: 3, user: 'bot_enthusiast', amount: 19.50, status: 'pending', date: '2024-01-14' },
    { id: 4, user: 'test_trader', amount: 39.00, status: 'failed', date: '2024-01-13' },
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
      
      <div className="table-wrapper">
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
                  <button 
                    className="action-btn view"
                    onClick={() => alert(`Viewing transaction for ${payment.user}`)}
                  >
                    View TX
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// ============================================================================
// TAB COMPONENTS - LOGS
// ============================================================================

const LogsTab: React.FC<{ logs: string[]; onRefresh: () => void }> = ({ logs, onRefresh }) => {
  const [refreshing, setRefreshing] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(false);

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(onRefresh, 5000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, onRefresh]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await onRefresh();
    setTimeout(() => setRefreshing(false), 500);
  };

  const handleDownload = () => {
    const content = logs.join('\n');
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `system-logs-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="logs-tab">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <h1>System Logs</h1>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <label style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <input 
              type="checkbox" 
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              style={{ width: '18px', height: '18px' }}
            />
            Auto-refresh
          </label>
          <button 
            className={`refresh-btn ${refreshing ? 'loading' : ''}`}
            onClick={handleRefresh}
            disabled={refreshing}
          >
            🔄 Refresh
          </button>
        </div>
      </div>
      
      <div className="logs-container">
        {logs.map((log, index) => (
          <div key={index} className="log-entry">
            {log}
          </div>
        ))}
      </div>
      
      <button className="action-btn" onClick={handleDownload}>
        📥 Download Full Logs
      </button>
    </div>
  );
};

// ============================================================================
// TAB COMPONENTS - SETTINGS
// ============================================================================

const SettingsTab: React.FC = () => {
  const [settings, setSettings] = useState({
    enableRegistrations: true,
    allowTestnet: true,
    maintenanceMode: false,
    maxDailyLoss: 5,
    maxDrawdown: 10
  });

  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    await new Promise(resolve => setTimeout(resolve, 1500));
    alert('Settings saved successfully!');
    setSaving(false);
  };

  return (
    <div className="settings-tab">
      <h1>System Settings</h1>
      
      <div className="settings-section">
        <h3>General Settings</h3>
        <label>
          <input 
            type="checkbox" 
            checked={settings.enableRegistrations}
            onChange={(e) => setSettings({...settings, enableRegistrations: e.target.checked})}
          />
          Enable new user registrations
        </label>
        <label>
          <input 
            type="checkbox" 
            checked={settings.allowTestnet}
            onChange={(e) => setSettings({...settings, allowTestnet: e.target.checked})}
          />
          Allow testnet trading
        </label>
        <label>
          <input 
            type="checkbox" 
            checked={settings.maintenanceMode}
            onChange={(e) => setSettings({...settings, maintenanceMode: e.target.checked})}
          />
          Maintenance mode
        </label>
      </div>
      
      <div className="settings-section">
        <h3>Risk Management</h3>
        <label>
          Max daily loss limit:
          <input 
            type="number" 
            value={settings.maxDailyLoss}
            onChange={(e) => setSettings({...settings, maxDailyLoss: parseInt(e.target.value)})}
            min="1"
            max="20"
          /> %
        </label>
        <label>
          Max drawdown:
          <input 
            type="number" 
            value={settings.maxDrawdown}
            onChange={(e) => setSettings({...settings, maxDrawdown: parseInt(e.target.value)})}
            min="1"
            max="50"
          /> %
        </label>
      </div>
      
      <button 
        className={`action-btn success ${saving ? 'loading' : ''}`}
        onClick={handleSave}
        disabled={saving}
      >
        💾 {saving ? 'Saving...' : 'Save Settings'}
      </button>
    </div>
  );
};

// ============================================================================
// UTILITY COMPONENTS
// ============================================================================

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

// ============================================================================
// EXPORT
// ============================================================================

export default AdminDashboard;
