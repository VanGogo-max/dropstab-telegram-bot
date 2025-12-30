// i18n.ts - Internationalization Configuration
import { useState, useEffect, createContext, useContext } from 'react';

// Supported languages
export const LANGUAGES = {
  en: {
    code: 'en',
    name: 'English',
    flag: '🇬🇧',
    nativeName: 'English'
  },
  ru: {
    code: 'ru',
    name: 'Russian',
    flag: '🇷🇺',
    nativeName: 'Русский'
  },
  zh: {
    code: 'zh',
    name: 'Chinese',
    flag: '🇨🇳',
    nativeName: '中文'
  },
  es: {
    code: 'es',
    name: 'Spanish',
    flag: '🇪🇸',
    nativeName: 'Español'
  },
  hi: {
    code: 'hi',
    name: 'Hindi',
    flag: '🇮🇳',
    nativeName: 'हिन्दी'
  },
  bg: {
    code: 'bg',
    name: 'Bulgarian',
    flag: '🇧🇬',
    nativeName: 'Български'
  }
};

// Translation keys structure
export interface Translations {
  // Navigation
  nav: {
    dashboard: string;
    bots: string;
    apiKeys: string;
    tradeHistory: string;
    referrals: string;
    settings: string;
    logout: string;
  };

  // Authentication
  auth: {
    login: string;
    register: string;
    email: string;
    password: string;
    name: string;
    referralCode: string;
    loginButton: string;
    registerButton: string;
    forgotPassword: string;
    alreadyHaveAccount: string;
    dontHaveAccount: string;
  };

  // Dashboard
  dashboard: {
    title: string;
    totalPnL: string;
    activeBots: string;
    totalTrades: string;
    winRate: string;
    todayPnL: string;
    weeklyPnL: string;
    monthlyPnL: string;
  };

  // Bots
  bots: {
    title: string;
    selectBot: string;
    configure: string;
    start: string;
    stop: string;
    pause: string;
    running: string;
    stopped: string;
    paused: string;
    error: string;
  };

  // Bot names
  botNames: {
    grid_trading: string;
    dca: string;
    momentum: string;
    mean_reversion: string;
    aggressive_scalper: string;
    arbitrage: string;
    futures_long_short: string;
    market_making: string;
    swing_trading: string;
    trend_following: string;
  };

  // API Keys
  apiKeys: {
    title: string;
    addKeys: string;
    saveKeys: string;
    deleteKeys: string;
    exchange: string;
    apiKey: string;
    apiSecret: string;
    validated: string;
    notValidated: string;
  };

  // Trade History
  tradeHistory: {
    title: string;
    date: string;
    bot: string;
    symbol: string;
    type: string;
    amount: string;
    price: string;
    total: string;
    fee: string;
    pnl: string;
    buy: string;
    sell: string;
    filters: string;
    export: string;
  };

  // Referrals
  referrals: {
    title: string;
    yourCode: string;
    totalReferrals: string;
    activeReferrals: string;
    totalEarnings: string;
    copyCode: string;
    shareVia: string;
    freeAfter: string;
    referralsNeeded: string;
  };

  // Settings
  settings: {
    title: string;
    profile: string;
    security: string;
    notifications: string;
    language: string;
    theme: string;
    save: string;
    cancel: string;
  };

  // Common
  common: {
    loading: string;
    save: string;
    cancel: string;
    delete: string;
    edit: string;
    confirm: string;
    success: string;
    error: string;
    warning: string;
    info: string;
    yes: string;
    no: string;
    search: string;
    filter: string;
    export: string;
    import: string;
    refresh: string;
    close: string;
  };

  // Onboarding
  onboarding: {
    welcome: string;
    skip: string;
    next: string;
    previous: string;
    finish: string;
    getStarted: string;
    step: string;
    of: string;
  };
}

// Language Context
interface LanguageContextType {
  language: string;
  setLanguage: (lang: string) => void;
  t: (key: string) => string;
}

export const LanguageContext = createContext<LanguageContextType>({
  language: 'en',
  setLanguage: () => {},
  t: (key) => key
});

// Get nested translation
export const getTranslation = (translations: any, key: string): string => {
  const keys = key.split('.');
  let value = translations;
  
  for (const k of keys) {
    if (value && typeof value === 'object' && k in value) {
      value = value[k];
    } else {
      return key; // Return key if translation not found
    }
  }
  
  return typeof value === 'string' ? value : key;
};

// Detect browser language
export const detectBrowserLanguage = (): string => {
  const browserLang = navigator.language.split('-')[0];
  return Object.keys(LANGUAGES).includes(browserLang) ? browserLang : 'en';
};

// Custom hook for translations
export const useTranslation = () => {
  return useContext(LanguageContext);
};

// Storage key
export const LANGUAGE_STORAGE_KEY = 'cryptobot_language';

// Get saved language
export const getSavedLanguage = (): string => {
  const saved = localStorage.getItem(LANGUAGE_STORAGE_KEY);
  return saved && Object.keys(LANGUAGES).includes(saved) ? saved : detectBrowserLanguage();
};

// Save language
export const saveLanguage = (lang: string): void => {
  if (Object.keys(LANGUAGES).includes(lang)) {
    localStorage.setItem(LANGUAGE_STORAGE_KEY, lang);
  }
};

export default {
  LANGUAGES,
  detectBrowserLanguage,
  getSavedLanguage,
  saveLanguage,
  getTranslation
};
