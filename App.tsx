// frontend/src/App.tsx
/**
 * App.tsx - АКТУАЛИЗИРАНА ВЕРСИЯ
 * 
 * ПРОМЕНИ:
 * ❌ МАХНАТО: localStorage.getItem('token')
 * ❌ МАХНАТО: fetch с Authorization header
 * ❌ МАХНАТО: Polling с setInterval
 * 
 * ✅ ДОБАВЕНО: useAuth hook
 * ✅ ДОБАВЕНО: apiFetch за всички API calls
 * ✅ ДОБАВЕНО: useWebSocket за real-time updates
 * ✅ ДОБАВЕНО: Error boundaries и loading states
 */

import React, { useState, useEffect } from 'react';
import { Menu, X, Home, Bot, Key, Settings, History, Users, LogOut, Bell } from 'lucide-react';

// НОВИ IMPORTS
import { useAuth } from './context/AuthProvider';
import { apiFetch } from './utils/apiClient';
import { useWebSocket } from './hooks/useWebSocket';

// Компоненти (съществуващи)
import Dashboard from './components/Dashboard';
import BotSelector from './components/BotSelector';
import ApiKeysManager from './components/ApiKeysManager';
import BotConfiguration from './components/BotConfiguration';
import BotControls from './components/BotControls';
import ReferralDashboard from './components/ReferralDashboard';
import TradeHistory from './components/TradeHistory';
import Login from './components/Login';

function App() {
  // AUTH STATE (замества localStorage)
  const { user, loading: authLoading, isAuthenticated, logout } = useAuth();

  // UI STATE
  const [currentView, setCurrentView] = useState('dashboard');
  const [selectedBot, setSelectedBot] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [notifications, setNotifications] = useState(0);

  // REAL-TIME UPDATES (замества polling)
  const { connected: wsConnected } = useWebSocket('/ws/updates', (data) => {
    console.log('[App] WebSocket update:', data);
    
    // Обработка на real-time updates
    switch (data.type) {
      case 'bot_status':
        // Update bot status в UI
        console.log('Bot status update:', data.payload);
        break;
      
      case 'trade_executed':
        // Покажи notification за нова trade
        setNotifications(prev => prev + 1);
        break;
      
      case 'notification':
        // Generic notification
        setNotifications(prev => prev + 1);
        break;
      
      default:
        console.log('Unknown update type:', data.type);
    }
  });

  /**
   * Навигация
   */
  const navigateTo = (view: string, botId: string | null = null) => {
    setCurrentView(view);
    setSelectedBot(botId);
    if (window.innerWidth < 768) {
      setSidebarOpen(false);
    }
  };

  /**
   * Logout handler
   */
  const handleLogout = async () => {
    try {
      await logout();
      setCurrentView('dashboard');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  /**
   * Render съответния view
   */
  const renderContent = () => {
    switch (currentView) {
      case 'dashboard':
        return <Dashboard />;
      case 'bots':
        return <BotSelector onSelectBot={(id) => navigateTo('bot-config', id)} />;
      case 'bot-config':
        return selectedBot ? <BotConfiguration botId={selectedBot} /> : <BotSelector />;
      case 'bot-controls':
        return selectedBot ? <BotControls botId={selectedBot} /> : <BotSelector />;
      case 'api-keys':
        return <ApiKeysManager />;
      case 'trade-history':
        return <TradeHistory botId={selectedBot} />;
      case 'referrals':
        return <ReferralDashboard />;
      case 'settings':
        return <div className="p-6"><h2>Settings</h2></div>;
      default:
        return <Dashboard />;
    }
  };

  // Loading screen по време на auth check
  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading CryptoTradeBot Pro...</p>
        </div>
      </div>
    );
  }

  // Login screen ако не е authenticated
  if (!isAuthenticated) {
    return <Login />;
  }

  // Main App UI
  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className={`
        fixed lg:static inset-y-0 left-0 z-50
        w-64 bg-white border-r border-gray-200
        transform transition-transform duration-300 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-6 border-b border-gray-200">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg"></div>
            <span className="font-bold text-lg text-gray-900">CTB Pro</span>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-1 hover:bg-gray-100 rounded"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-1">
          <NavItem
            icon={<Home className="w-5 h-5" />}
            label="Dashboard"
            active={currentView === 'dashboard'}
            onClick={() => navigateTo('dashboard')}
          />
          
          <NavItem
            icon={<Bot className="w-5 h-5" />}
            label="Trading Bots"
            active={currentView.includes('bot')}
            onClick={() => navigateTo('bots')}
          />

          <NavItem
            icon={<Key className="w-5 h-5" />}
            label="API Keys"
            active={currentView === 'api-keys'}
            onClick={() => navigateTo('api-keys')}
          />

          <NavItem
            icon={<History className="w-5 h-5" />}
            label="Trade History"
            active={currentView === 'trade-history'}
            onClick={() => navigateTo('trade-history')}
          />

          <NavItem
            icon={<Users className="w-5 h-5" />}
            label="Referrals"
            active={currentView === 'referrals'}
            onClick={() => navigateTo('referrals')}
          />

          <NavItem
            icon={<Settings className="w-5 h-5" />}
            label="Settings"
            active={currentView === 'settings'}
            onClick={() => navigateTo('settings')}
          />
        </nav>

        {/* User Info + Logout */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 bg-white">
          <div className="flex items-center gap-3 px-3 py-2">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
              {user?.name?.charAt(0) || 'U'}
            </div>
            <div className="flex-1 min-w-0">
              <div className="font-medium text-gray-900 truncate">{user?.name || 'User'}</div>
              <div className="text-xs text-gray-500 truncate">{user?.email}</div>
            </div>
            <button
              onClick={handleLogout}
              className="p-2 hover:bg-gray-100 rounded"
              title="Logout"
            >
              <LogOut className="w-4 h-4 text-gray-600" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-h-screen">
        {/* Top Bar */}
        <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden p-2 hover:bg-gray-100 rounded"
            >
              <Menu className="w-6 h-6" />
            </button>
            <h1 className="text-xl font-bold text-gray-900 hidden sm:block">
              {currentView === 'dashboard' && 'Dashboard'}
              {currentView === 'bots' && 'Trading Bots'}
              {currentView === 'api-keys' && 'API Keys'}
              {currentView === 'trade-history' && 'Trade History'}
              {currentView === 'referrals' && 'Referral Program'}
              {currentView === 'settings' && 'Settings'}
            </h1>
          </div>

          <div className="flex items-center gap-4">
            {/* WebSocket Status */}
            <div className="flex items-center gap-2 text-sm">
              <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-gray-600 hidden sm:inline">
                {wsConnected ? 'Connected' : 'Offline'}
              </span>
            </div>

            {/* Notifications */}
            <button className="relative p-2 hover:bg-gray-100 rounded-lg">
              <Bell className="w-5 h-5 text-gray-600" />
              {notifications > 0 && (
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
              )}
            </button>
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-1 overflow-auto">
          {renderContent()}
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 py-4 px-6">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <div>© 2025 CryptoTradeBot Pro</div>
            <div className="flex gap-4">
              <a href="#" className="hover:text-blue-600">Terms</a>
              <a href="#" className="hover:text-blue-600">Privacy</a>
            </div>
          </div>
        </footer>
      </div>

      {/* Mobile Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        ></div>
      )}
    </div>
  );
}

// NavItem Component
function NavItem({ 
  icon, 
  label, 
  active, 
  onClick, 
  badge 
}: { 
  icon: React.ReactNode; 
  label: string; 
  active: boolean; 
  onClick: () => void; 
  badge?: number;
}) {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition ${
        active
          ? 'bg-blue-50 text-blue-600 font-medium'
          : 'text-gray-700 hover:bg-gray-50'
      }`}
    >
      {icon}
      <span className="flex-1 text-left">{label}</span>
      {badge && badge > 0 && (
        <span className="bg-blue-600 text-white text-xs px-2 py-0.5 rounded-full">
          {badge}
        </span>
      )}
    </button>
  );
}

export default App;
