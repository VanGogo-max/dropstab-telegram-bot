// mobile/App.tsx - React Native Mobile Application
import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  RefreshControl,
  StatusBar,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

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

const API_URL = 'https://your-api.com'; // Change this

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentScreen, setCurrentScreen] = useState('dashboard');
  const [bots, setBots] = useState<Bot[]>([]);
  const [performance, setPerformance] = useState<Performance | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [token, setToken] = useState('');

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const savedToken = await AsyncStorage.getItem('token');
    if (savedToken) {
      setToken(savedToken);
      setIsAuthenticated(true);
      fetchData();
    }
  };

  const fetchData = async () => {
    await Promise.all([fetchBots(), fetchPerformance()]);
  };

  const fetchBots = async () => {
    try {
      const response = await fetch(`${API_URL}/api/bots/status`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setBots(Object.values(data.bots));
    } catch (error) {
      console.error('Error fetching bots:', error);
    }
  };

  const fetchPerformance = async () => {
    try {
      const response = await fetch(`${API_URL}/api/performance`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setPerformance(data);
    } catch (error) {
      console.error('Error fetching performance:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchData();
    setRefreshing(false);
  };

  if (!isAuthenticated) {
    return <LoginScreen onLogin={(newToken) => {
      setToken(newToken);
      setIsAuthenticated(true);
    }} />;
  }

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#0a0a0f" />
      
      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {currentScreen === 'dashboard' && (
          <DashboardScreen performance={performance} bots={bots} />
        )}
        
        {currentScreen === 'bots' && (
          <BotsScreen bots={bots} onRefresh={fetchBots} />
        )}
        
        {currentScreen === 'performance' && (
          <PerformanceScreen performance={performance} />
        )}
        
        {currentScreen === 'settings' && (
          <SettingsScreen onLogout={() => {
            AsyncStorage.removeItem('token');
            setIsAuthenticated(false);
          }} />
        )}
      </ScrollView>

      <BottomNav currentScreen={currentScreen} setScreen={setCurrentScreen} />
    </View>
  );
}

// Login Screen
const LoginScreen: React.FC<{ onLogin: (token: string) => void }> = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async () => {
    try {
      const response = await fetch(`${API_URL}/api/user/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await response.json();
      
      if (data.token) {
        await AsyncStorage.setItem('token', data.token);
        onLogin(data.token);
      } else {
        Alert.alert('Error', 'Invalid credentials');
      }
    } catch (error) {
      Alert.alert('Error', 'Login failed');
    }
  };

  return (
    <View style={styles.loginContainer}>
      <Text style={styles.loginTitle}>🚀 CryptoTradeBot Pro</Text>
      
      <TextInput
        style={styles.input}
        placeholder="Email"
        placeholderTextColor="#666"
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        keyboardType="email-address"
      />
      
      <TextInput
        style={styles.input}
        placeholder="Password"
        placeholderTextColor="#666"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
      
      <TouchableOpacity style={styles.loginButton} onPress={handleLogin}>
        <Text style={styles.loginButtonText}>Login</Text>
      </TouchableOpacity>
    </View>
  );
};

// Dashboard Screen
const DashboardScreen: React.FC<{ performance: Performance | null; bots: Bot[] }> = 
  ({ performance, bots }) => {
  
  return (
    <View style={styles.screen}>
      <Text style={styles.screenTitle}>Dashboard</Text>
      
      <View style={styles.statsGrid}>
        <StatCard 
          title="Total P&L" 
          value={`$${performance?.totalProfit.toFixed(2) || '0.00'}`}
          trend="+12.5%"
          positive={true}
        />
        <StatCard 
          title="Active Bots" 
          value={`${performance?.activeBots || 0}`}
        />
        <StatCard 
          title="Total Trades" 
          value={`${performance?.totalTrades || 0}`}
        />
        <StatCard 
          title="Win Rate" 
          value={`${((performance?.winRate || 0) * 100).toFixed(1)}%`}
          positive={true}
        />
      </View>
      
      <Text style={styles.sectionTitle}>Active Bots</Text>
      {bots.length > 0 ? (
        bots.map(bot => <BotCard key={bot.id} bot={bot} />)
      ) : (
        <Text style={styles.emptyText}>No active bots</Text>
      )}
    </View>
  );
};

// Bots Screen
const BotsScreen: React.FC<{ bots: Bot[]; onRefresh: () => void }> = ({ bots, onRefresh }) => {
  const botTypes = [
    { id: 'dca', name: 'DCA Bot', icon: '🔄' },
    { id: 'signal', name: 'Signal Bot', icon: '📊' },
    { id: 'portfolio', name: 'Portfolio', icon: '💼' },
    { id: 'trailing', name: 'Trailing Stop', icon: '🎯' },
    { id: 'arbitrage', name: 'Arbitrage', icon: '⚖️' },
  ];

  const startBot = (type: string) => {
    Alert.alert('Start Bot', `Starting ${type} bot...`);
    // TODO: Implement bot start
  };

  return (
    <View style={styles.screen}>
      <Text style={styles.screenTitle}>Bots Manager</Text>
      
      <Text style={styles.sectionTitle}>Start New Bot</Text>
      <View style={styles.botTypesGrid}>
        {botTypes.map(type => (
          <TouchableOpacity
            key={type.id}
            style={styles.botTypeCard}
            onPress={() => startBot(type.id)}
          >
            <Text style={styles.botTypeIcon}>{type.icon}</Text>
            <Text style={styles.botTypeName}>{type.name}</Text>
            <Text style={styles.startText}>Start →</Text>
          </TouchableOpacity>
        ))}
      </View>
      
      <Text style={styles.sectionTitle}>Active Bots</Text>
      {bots.map(bot => (
        <View key={bot.id} style={styles.activeBotItem}>
          <View>
            <Text style={styles.activeBotName}>{bot.type.toUpperCase()}</Text>
            <Text style={styles.activeBotStatus}>{bot.status}</Text>
          </View>
          <TouchableOpacity style={styles.stopButton}>
            <Text style={styles.stopButtonText}>Stop</Text>
          </TouchableOpacity>
        </View>
      ))}
    </View>
  );
};

// Performance Screen
const PerformanceScreen: React.FC<{ performance: Performance | null }> = ({ performance }) => {
  return (
    <View style={styles.screen}>
      <Text style={styles.screenTitle}>Performance</Text>
      
      <View style={styles.performanceCard}>
        <Text style={styles.performanceTitle}>Total Performance</Text>
        <Text style={styles.performanceValue}>
          ${performance?.totalProfit.toFixed(2) || '0.00'}
        </Text>
        <Text style={styles.performanceLabel}>Total Profit</Text>
      </View>
      
      <View style={styles.metricsContainer}>
        <MetricRow label="Total Trades" value={`${performance?.totalTrades || 0}`} />
        <MetricRow label="Win Rate" value={`${((performance?.winRate || 0) * 100).toFixed(1)}%`} />
        <MetricRow label="Active Bots" value={`${performance?.activeBots || 0}`} />
      </View>
    </View>
  );
};

// Settings Screen
const SettingsScreen: React.FC<{ onLogout: () => void }> = ({ onLogout }) => {
  return (
    <View style={styles.screen}>
      <Text style={styles.screenTitle}>Settings</Text>
      
      <TouchableOpacity style={styles.settingItem}>
        <Text style={styles.settingText}>💳 Subscription</Text>
      </TouchableOpacity>
      
      <TouchableOpacity style={styles.settingItem}>
        <Text style={styles.settingText}>🎁 Referral Program</Text>
      </TouchableOpacity>
      
      <TouchableOpacity style={styles.settingItem}>
        <Text style={styles.settingText}>🔔 Notifications</Text>
      </TouchableOpacity>
      
      <TouchableOpacity style={styles.settingItem}>
        <Text style={styles.settingText}>🔐 Security</Text>
      </TouchableOpacity>
      
      <TouchableOpacity style={[styles.settingItem, styles.logoutButton]} onPress={onLogout}>
        <Text style={styles.logoutText}>Logout</Text>
      </TouchableOpacity>
    </View>
  );
};

// Components
const StatCard: React.FC<{ title: string; value: string; trend?: string; positive?: boolean }> = 
  ({ title, value, trend, positive }) => {
  
  return (
    <View style={styles.statCard}>
      <Text style={styles.statTitle}>{title}</Text>
      <Text style={styles.statValue}>{value}</Text>
      {trend && (
        <Text style={[styles.statTrend, positive && styles.statTrendPositive]}>
          {trend}
        </Text>
      )}
    </View>
  );
};

const BotCard: React.FC<{ bot: Bot }> = ({ bot }) => {
  const statusColor = bot.status === 'running' ? '#10b981' : '#ef4444';
  
  return (
    <View style={styles.botCard}>
      <View style={styles.botCardHeader}>
        <Text style={styles.botCardTitle}>{bot.type.toUpperCase()} Bot</Text>
        <View style={[styles.statusDot, { backgroundColor: statusColor }]} />
      </View>
      <Text style={styles.botCardId}>ID: {bot.id}</Text>
    </View>
  );
};

const MetricRow: React.FC<{ label: string; value: string }> = ({ label, value }) => {
  return (
    <View style={styles.metricRow}>
      <Text style={styles.metricLabel}>{label}</Text>
      <Text style={styles.metricValue}>{value}</Text>
    </View>
  );
};

// Bottom Navigation
const BottomNav: React.FC<{ currentScreen: string; setScreen: (screen: string) => void }> = 
  ({ currentScreen, setScreen }) => {
  
  const tabs = [
    { id: 'dashboard', icon: '📊', label: 'Dashboard' },
    { id: 'bots', icon: '🤖', label: 'Bots' },
    { id: 'performance', icon: '📈', label: 'Stats' },
    { id: 'settings', icon: '⚙️', label: 'Settings' },
  ];

  return (
    <View style={styles.bottomNav}>
      {tabs.map(tab => (
        <TouchableOpacity
          key={tab.id}
          style={styles.navItem}
          onPress={() => setScreen(tab.id)}
        >
          <Text style={styles.navIcon}>{tab.icon}</Text>
          <Text style={[
            styles.navLabel,
            currentScreen === tab.id && styles.navLabelActive
          ]}>
            {tab.label}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  );
};

// Styles
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0f',
  },
  content: {
    flex: 1,
  },
  screen: {
    padding: 16,
    paddingBottom: 80,
  },
  screenTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#fff',
    marginTop: 20,
    marginBottom: 12,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  statCard: {
    flex: 1,
    minWidth: '45%',
    backgroundColor: '#12121a',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#2a2a3a',
  },
  statTitle: {
    fontSize: 12,
    color: '#9ca3af',
    marginBottom: 8,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  statTrend: {
    fontSize: 12,
    color: '#9ca3af',
    marginTop: 4,
  },
  statTrendPositive: {
    color: '#10b981',
  },
  botCard: {
    backgroundColor: '#12121a',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#2a2a3a',
    marginBottom: 12,
  },
  botCardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  botCardTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  botCardId: {
    fontSize: 12,
    color: '#9ca3af',
  },
  emptyText: {
    color: '#9ca3af',
    textAlign: 'center',
    marginTop: 20,
  },
  botTypesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  botTypeCard: {
    flex: 1,
    minWidth: '45%',
    backgroundColor: '#12121a',
    padding: 20,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#2a2a3a',
    alignItems: 'center',
  },
  botTypeIcon: {
    fontSize: 32,
    marginBottom: 8,
  },
  botTypeName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 8,
  },
  startText: {
    fontSize: 12,
    color: '#3b82f6',
  },
  activeBotItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#12121a',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#2a2a3a',
    marginBottom: 8,
  },
  activeBotName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
  },
  activeBotStatus: {
    fontSize: 12,
    color: '#9ca3af',
  },
  stopButton: {
    backgroundColor: '#ef4444',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 6,
  },
  stopButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
  performanceCard: {
    backgroundColor: '#12121a',
    padding: 32,
    borderRadius: 16,
    borderWidth: 2,
    borderColor: '#3b82f6',
    alignItems: 'center',
    marginBottom: 20,
  },
  performanceTitle: {
    fontSize: 14,
    color: '#9ca3af',
    marginBottom: 8,
  },
  performanceValue: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#10b981',
    marginBottom: 4,
  },
  performanceLabel: {
    fontSize: 12,
    color: '#9ca3af',
  },
  metricsContainer: {
    backgroundColor: '#12121a',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#2a2a3a',
  },
  metricRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#2a2a3a',
  },
  metricLabel: {
    fontSize: 14,
    color: '#9ca3af',
  },
  metricValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#fff',
  },
  settingItem: {
    backgroundColor: '#12121a',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#2a2a3a',
    marginBottom: 12,
  },
  settingText: {
    fontSize: 16,
    color: '#fff',
  },
  logoutButton: {
    backgroundColor: '#ef4444',
    marginTop: 20,
  },
  logoutText: {
    fontSize: 16,
    color: '#fff',
    fontWeight: '600',
    textAlign: 'center',
  },
  bottomNav: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    flexDirection: 'row',
    backgroundColor: '#12121a',
    borderTopWidth: 1,
    borderTopColor: '#2a2a3a',
    paddingBottom: 20,
    paddingTop: 12,
  },
  navItem: {
    flex: 1,
    alignItems: 'center',
  },
  navIcon: {
    fontSize: 24,
    marginBottom: 4,
  },
  navLabel: {
    fontSize: 10,
    color: '#9ca3af',
  },
  navLabelActive: {
    color: '#3b82f6',
  },
  loginContainer: {
    flex: 1,
    backgroundColor: '#0a0a0f',
    justifyContent: 'center',
    padding: 24,
  },
  loginTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
    marginBottom: 40,
  },
  input: {
    backgroundColor: '#12121a',
    borderWidth: 1,
    borderColor: '#2a2a3a',
    borderRadius: 12,
    padding: 16,
    color: '#fff',
    fontSize: 16,
    marginBottom: 16,
  },
  loginButton: {
    backgroundColor: '#3b82f6',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 8,
  },
  loginButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});
