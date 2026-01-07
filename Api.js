/**
 * api.js - API Service for CryptoTradeBot Frontend
 * Handles all communication with Python FastAPI backend
 */

// Backend URL - change this to your production URL
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Helper function for making API requests
 */
async function fetchAPI(endpoint, options = {}) {
  const url = `${API_URL}${endpoint}`;
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    
    // Parse response
    const data = await response.json();
    
    // Check for errors
    if (!response.ok) {
      throw new Error(data.detail || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    return data;
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error);
    throw error;
  }
}

/**
 * API Service Object
 */
export const api = {
  // ==================== ONBOARDING ====================
  
  /**
   * Complete onboarding and auto-start strategy
   * @param {string} userId - User ID
   * @param {object} profile - User profile from onboarding
   * @returns {Promise<object>} Response with started strategy
   */
  completeOnboarding: async (userId, profile) => {
    return fetchAPI('/api/onboarding/complete', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        profile: {
          capital: parseFloat(profile.capital),
          experience: profile.experience,
          risk_tolerance: profile.risk_tolerance || profile.risk,
          can_monitor: profile.can_monitor !== undefined ? profile.can_monitor : profile.monitor,
          goals: profile.goals || []
        }
      })
    });
  },

  // ==================== STRATEGY ====================
  
  /**
   * Get strategy recommendations without starting
   * @param {string} userId - User ID
   * @param {object} profile - User profile
   * @returns {Promise<object>} Top 3 recommended strategies
   */
  getRecommendations: async (userId, profile) => {
    return fetchAPI('/api/strategy/recommendations', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        profile: {
          capital: parseFloat(profile.capital),
          experience: profile.experience,
          risk_tolerance: profile.risk_tolerance || profile.risk,
          can_monitor: profile.can_monitor !== undefined ? profile.can_monitor : profile.monitor,
          goals: profile.goals || []
        }
      })
    });
  },

  // ==================== USER ====================
  
  /**
   * Get user profile
   * @param {string} userId - User ID
   * @returns {Promise<object>} User profile
   */
  getUserProfile: async (userId) => {
    return fetchAPI(`/api/user/${userId}/profile`);
  },

  /**
   * Check if user completed onboarding
   * @param {string} userId - User ID
   * @returns {Promise<object>} { completed: boolean }
   */
  checkOnboardingStatus: async (userId) => {
    try {
      return await fetchAPI(`/api/user/${userId}/onboarding-status`);
    } catch (error) {
      console.error('Check onboarding status error:', error);
      return { completed: false, user_id: userId };
    }
  },

  /**
   * Get active strategy for user
   * @param {string} userId - User ID
   * @returns {Promise<object>} Active strategy info
   */
  getActiveStrategy: async (userId) => {
    return fetchAPI(`/api/user/${userId}/active-strategy`);
  },

  // ==================== BOTS ====================
  
  /**
   * Start a bot manually
   * @param {string} userId - User ID
   * @param {string} botType - Bot type (e.g., 'grid', 'dca')
   * @param {object} config - Bot configuration
   */
  startBot: async (userId, botType, config) => {
    return fetchAPI(`/api/bots/${botType}/start`, {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        ...config
      })
    });
  },

  /**
   * Stop a bot
   * @param {string} userId - User ID
   * @param {string} botType - Bot type
   */
  stopBot: async (userId, botType) => {
    return fetchAPI(`/api/bots/${botType}/stop`, {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId
      })
    });
  },

  /**
   * Get bot status
   * @param {string} userId - User ID
   * @param {string} botType - Bot type
   */
  getBotStatus: async (userId, botType) => {
    return fetchAPI(`/api/bots/status/all?user_id=${userId}`);
  },

  // ==================== PERFORMANCE ====================
  
  /**
   * Get total performance
   * @param {string} userId - User ID
   */
  getPerformance: async (userId) => {
    return fetchAPI(`/api/performance/total?user_id=${userId}`);
  },

  // ==================== HEALTH ====================
  
  /**
   * Check API health
   */
  healthCheck: async () => {
    return fetchAPI('/health');
  },

  /**
   * Get system status
   */
  getStatus: async () => {
    return fetchAPI('/status');
  }
};

// Export API_URL for reference
export { API_URL };

// Default export
export default api;
