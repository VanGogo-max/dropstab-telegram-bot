import React, { useState, useRef, useEffect } from 'react';
import { Globe, Check, ChevronDown } from 'lucide-react';
import { LANGUAGES, useTranslation } from './i18n';

const LanguageSwitcher = ({ className = '' }) => {
  const { language, setLanguage } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const currentLang = LANGUAGES[language as keyof typeof LANGUAGES] || LANGUAGES.en;

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLanguageChange = (langCode: string) => {
    setLanguage(langCode);
    setIsOpen(false);
  };

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 rounded-lg border-2 border-gray-200 hover:border-blue-500 transition bg-white"
        aria-label="Select language"
      >
        <Globe className="w-5 h-5 text-gray-600" />
        <span className="text-2xl">{currentLang.flag}</span>
        <span className="font-medium text-gray-900 hidden sm:inline">
          {currentLang.nativeName}
        </span>
        <ChevronDown className={`w-4 h-4 text-gray-600 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-xl border-2 border-gray-200 overflow-hidden z-50 animate-slideDown">
          <div className="p-2 bg-gray-50 border-b border-gray-200">
            <p className="text-xs font-medium text-gray-600 uppercase px-2">
              Select Language
            </p>
          </div>

          <div className="max-h-80 overflow-y-auto">
            {Object.entries(LANGUAGES).map(([code, lang]) => {
              const isSelected = code === language;
              
              return (
                <button
                  key={code}
                  onClick={() => handleLanguageChange(code)}
                  className={`w-full flex items-center justify-between px-4 py-3 hover:bg-blue-50 transition ${
                    isSelected ? 'bg-blue-50' : ''
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{lang.flag}</span>
                    <div className="text-left">
                      <div className="font-medium text-gray-900">
                        {lang.nativeName}
                      </div>
                      <div className="text-xs text-gray-500">
                        {lang.name}
                      </div>
                    </div>
                  </div>
                  
                  {isSelected && (
                    <Check className="w-5 h-5 text-blue-600" />
                  )}
                </button>
              );
            })}
          </div>

          {/* Footer with stats */}
          <div className="p-3 bg-gray-50 border-t border-gray-200">
            <p className="text-xs text-gray-500 text-center">
              {Object.keys(LANGUAGES).length} languages supported
            </p>
          </div>
        </div>
      )}

      {/* CSS Animation */}
      <style>{`
        @keyframes slideDown {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .animate-slideDown {
          animation: slideDown 0.2s ease-out;
        }
      `}</style>
    </div>
  );
};

// Compact version for mobile
export const LanguageSwitcherCompact = () => {
  const { language, setLanguage } = useTranslation();
  const currentLang = LANGUAGES[language as keyof typeof LANGUAGES] || LANGUAGES.en;

  return (
    <select
      value={language}
      onChange={(e) => setLanguage(e.target.value)}
      className="px-3 py-2 rounded-lg border-2 border-gray-200 bg-white text-gray-900 font-medium focus:border-blue-500 focus:outline-none"
    >
      {Object.entries(LANGUAGES).map(([code, lang]) => (
        <option key={code} value={code}>
          {lang.flag} {lang.nativeName}
        </option>
      ))}
    </select>
  );
};

export default LanguageSwitcher;
