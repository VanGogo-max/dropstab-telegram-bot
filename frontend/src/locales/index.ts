// ============================================================================
// frontend/src/locales/index.ts - i18n Configuration & Loader
// ============================================================================

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import all translation files
import bg from './bg.json';
import en from './en.json';
import ru from './ru.json';
import es from './es.json';
import de from './de.json';
import fr from './fr.json';
import it from './it.json';
import pt from './pt.json';
import tr from './tr.json';
import ar from './ar.json';

// Language resources
const resources = {
  bg: { translation: bg },
  en: { translation: en },
  ru: { translation: ru },
  es: { translation: es },
  de: { translation: de },
  fr: { translation: fr },
  it: { translation: it },
  pt: { translation: pt },
  tr: { translation: tr },
  ar: { translation: ar },
};

// Supported languages configuration
export const languages = [
  { code: 'bg', name: 'Български', flag: '🇧🇬' },
  { code: 'en', name: 'English', flag: '🇬🇧' },
  { code: 'ru', name: 'Русский', flag: '🇷🇺' },
  { code: 'es', name: 'Español', flag: '🇪🇸' },
  { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
  { code: 'fr', name: 'Français', flag: '🇫🇷' },
  { code: 'it', name: 'Italiano', flag: '🇮🇹' },
  { code: 'pt', name: 'Português', flag: '🇵🇹' },
  { code: 'tr', name: 'Türkçe', flag: '🇹🇷' },
  { code: 'ar', name: 'العربية', flag: '🇸🇦', rtl: true },
];

// Initialize i18next
i18n
  .use(LanguageDetector) // Detect user language
  .use(initReactI18next) // Pass i18n to react-i18next
  .init({
    resources,
    fallbackLng: 'en', // Default language
    defaultNS: 'translation',
    
    // Language detection options
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
      lookupLocalStorage: 'i18nextLng',
    },

    interpolation: {
      escapeValue: false, // React already escapes values
    },

    react: {
      useSuspense: true,
    },

    // Debug mode (disable in production)
    debug: import.meta.env.DEV,
  });

// Helper function to change language
export const changeLanguage = (languageCode: string) => {
  i18n.changeLanguage(languageCode);
  
  // Set document direction for RTL languages
  const lang = languages.find(l => l.code === languageCode);
  document.documentElement.dir = lang?.rtl ? 'rtl' : 'ltr';
  document.documentElement.lang = languageCode;
};

// Get current language info
export const getCurrentLanguage = () => {
  const currentLang = i18n.language || 'en';
  return languages.find(l => l.code === currentLang) || languages[1];
};

export default i18n;


// ============================================================================
// Usage Example Component: LanguageSelector.tsx
// ============================================================================

/*
import React from 'react';
import { useTranslation } from 'react-i18next';
import { languages, changeLanguage, getCurrentLanguage } from '@/locales';
import { Globe } from 'lucide-react';

export const LanguageSelector: React.FC = () => {
  const { t } = useTranslation();
  const currentLang = getCurrentLanguage();
  const [isOpen, setIsOpen] = React.useState(false);

  const handleLanguageChange = (code: string) => {
    changeLanguage(code);
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white border border-gray-200 hover:bg-gray-50"
      >
        <Globe className="w-4 h-4" />
        <span>{currentLang.flag} {currentLang.name}</span>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
          {languages.map((lang) => (
            <button
              key={lang.code}
              onClick={() => handleLanguageChange(lang.code)}
              className={`w-full text-left px-4 py-2 hover:bg-gray-100 flex items-center gap-2 ${
                currentLang.code === lang.code ? 'bg-blue-50 font-semibold' : ''
              }`}
            >
              <span>{lang.flag}</span>
              <span>{lang.name}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
*/


// ============================================================================
// Usage in Components
// ============================================================================

/*
import { useTranslation } from 'react-i18next';

const MyComponent = () => {
  const { t } = useTranslation();
  
  return (
    <div>
      <h1>{t('dashboard.title')}</h1>
      <p>{t('dashboard.balance')}: ${balance}</p>
      <button>{t('trading.buy')}</button>
    </div>
  );
};
*/


// ============================================================================
// Main App Setup: App.tsx
// ============================================================================

/*
import React, { Suspense } from 'react';
import './locales'; // Import i18n configuration

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <YourAppComponents />
    </Suspense>
  );
}
*/


// ============================================================================
// Package Dependencies (add to package.json)
// ============================================================================

/*
{
  "dependencies": {
    "i18next": "^23.7.6",
    "react-i18next": "^13.5.0",
    "i18next-browser-languagedetector": "^7.2.0"
  }
}

Install with:
npm install i18next react-i18next i18next-browser-languagedetector
*/
