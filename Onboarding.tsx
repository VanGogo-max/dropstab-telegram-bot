import React, { useState, useEffect } from 'react';
import { X, ChevronRight, ChevronLeft, Check, Key, Bot, TrendingUp, Users, Zap } from 'lucide-react';

const ONBOARDING_STEPS = [
  {
    id: 'welcome',
    title: 'Welcome to CryptoTradeBot Pro',
    description: 'Automate your crypto trading with 10+ professional strategies',
    icon: Zap,
    content: 'CryptoTradeBot Pro helps you trade 24/7 with proven strategies. No coding required - just configure and start earning!',
    highlights: [],
    action: 'Get Started'
  },
  {
    id: 'api-keys',
    title: 'Connect Your Exchange',
    description: 'Securely link your trading accounts',
    icon: Key,
    content: 'Add API keys from KCEX, Hyperliquid, or Uniswap. All keys are encrypted with AES-256. We never store withdrawal permissions.',
    highlights: ['#api-keys-button'],
    action: 'Add API Keys'
  },
  {
    id: 'bots',
    title: 'Choose Your Strategy',
    description: 'Select from 10 trading bots',
    icon: Bot,
    content: 'Grid Trading, DCA, Scalping, Arbitrage, and more. Each bot has different risk levels and profit targets. Start with conservative strategies.',
    highlights: ['#bot-selector'],
    action: 'Browse Bots'
  },
  {
    id: 'configure',
    title: 'Configure & Launch',
    description: 'Set parameters and start trading',
    icon: TrendingUp,
    content: 'Adjust position sizes, stop losses, and take profits. Use Conservative preset for beginners. You can always pause or stop anytime.',
    highlights: ['#bot-configuration'],
    action: 'Configure Bot'
  },
  {
    id: 'referral',
    title: 'Earn Free Access',
    description: 'Refer 10 friends for lifetime FREE',
    icon: Users,
    content: '$10/month subscription, or get it FREE with 10 referrals! Earn $1 per referral. Share your code with friends and traders.',
    highlights: ['#referral-button'],
    action: 'Get Referral Code'
  }
];

const Onboarding = ({ onComplete, onSkip }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [completed, setCompleted] = useState(false);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Check if user has completed onboarding
    const hasCompleted = localStorage.getItem('onboarding_completed');
    if (!hasCompleted) {
      setTimeout(() => setIsVisible(true), 500);
    }
  }, []);

  useEffect(() => {
    // Highlight elements
    const step = ONBOARDING_STEPS[currentStep];
    if (step.highlights.length > 0) {
      step.highlights.forEach(selector => {
        const element = document.querySelector(selector);
        if (element) {
          element.classList.add('onboarding-highlight');
        }
      });
    }

    return () => {
      // Remove highlights
      document.querySelectorAll('.onboarding-highlight').forEach(el => {
        el.classList.remove('onboarding-highlight');
      });
    };
  }, [currentStep]);

  const handleNext = () => {
    if (currentStep < ONBOARDING_STEPS.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleComplete();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = () => {
    setCompleted(true);
    localStorage.setItem('onboarding_completed', 'true');
    setTimeout(() => {
      setIsVisible(false);
      onComplete?.();
    }, 1000);
  };

  const handleSkip = () => {
    localStorage.setItem('onboarding_completed', 'true');
    setIsVisible(false);
    onSkip?.();
  };

  if (!isVisible) return null;

  const step = ONBOARDING_STEPS[currentStep];
  const Icon = step.icon;
  const progress = ((currentStep + 1) / ONBOARDING_STEPS.length) * 100;

  return (
    <>
      {/* Overlay */}
      <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fadeIn">
        {/* Modal */}
        <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full overflow-hidden animate-slideUp">
          {/* Header */}
          <div className="relative bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-white">
            <button
              onClick={handleSkip}
              className="absolute top-4 right-4 p-2 hover:bg-white/20 rounded-lg transition"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-4 mb-4">
              <div className="w-16 h-16 bg-white/20 rounded-xl flex items-center justify-center">
                <Icon className="w-8 h-8" />
              </div>
              <div>
                <div className="text-sm text-blue-100 mb-1">
                  Step {currentStep + 1} of {ONBOARDING_STEPS.length}
                </div>
                <h2 className="text-2xl font-bold">{step.title}</h2>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-white/20 rounded-full h-2">
              <div
                className="bg-white h-2 rounded-full transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>

          {/* Content */}
          <div className="p-8">
            {!completed ? (
              <>
                <p className="text-lg text-gray-600 mb-2">{step.description}</p>
                <p className="text-gray-700 leading-relaxed mb-6">{step.content}</p>

                {/* Feature Highlights */}
                {currentStep === 0 && (
                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <div className="font-bold text-blue-900 mb-1">10+ Strategies</div>
                      <div className="text-sm text-blue-700">Professional bots</div>
                    </div>
                    <div className="bg-green-50 p-4 rounded-lg">
                      <div className="font-bold text-green-900 mb-1">24/7 Trading</div>
                      <div className="text-sm text-green-700">Never miss opportunities</div>
                    </div>
                    <div className="bg-purple-50 p-4 rounded-lg">
                      <div className="font-bold text-purple-900 mb-1">Bank-Level Security</div>
                      <div className="text-sm text-purple-700">AES-256 encryption</div>
                    </div>
                    <div className="bg-orange-50 p-4 rounded-lg">
                      <div className="font-bold text-orange-900 mb-1">Free Option</div>
                      <div className="text-sm text-orange-700">10 referrals = FREE</div>
                    </div>
                  </div>
                )}

                {/* Referral Highlight */}
                {currentStep === 4 && (
                  <div className="bg-gradient-to-r from-green-50 to-blue-50 border-2 border-green-200 rounded-lg p-6 mb-6">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center text-white font-bold text-xl">
                        $1
                      </div>
                      <div>
                        <div className="font-bold text-gray-900">Per Referral</div>
                        <div className="text-sm text-gray-600">Instant credit</div>
                      </div>
                    </div>
                    <div className="text-center py-3">
                      <div className="text-4xl font-bold text-gray-900 mb-1">10 Referrals</div>
                      <div className="text-lg text-gray-600">= FREE Lifetime Access 🎉</div>
                    </div>
                  </div>
                )}

                {/* Progress Dots */}
                <div className="flex justify-center gap-2 mb-6">
                  {ONBOARDING_STEPS.map((_, index) => (
                    <div
                      key={index}
                      className={`h-2 rounded-full transition-all ${
                        index === currentStep
                          ? 'w-8 bg-blue-600'
                          : index < currentStep
                          ? 'w-2 bg-green-500'
                          : 'w-2 bg-gray-300'
                      }`}
                    />
                  ))}
                </div>

                {/* Navigation */}
                <div className="flex justify-between items-center gap-4">
                  <button
                    onClick={handleSkip}
                    className="px-6 py-3 text-gray-600 hover:bg-gray-100 rounded-lg transition"
                  >
                    Skip Tutorial
                  </button>

                  <div className="flex gap-3">
                    {currentStep > 0 && (
                      <button
                        onClick={handlePrevious}
                        className="px-6 py-3 border-2 border-gray-300 rounded-lg hover:bg-gray-50 transition flex items-center gap-2"
                      >
                        <ChevronLeft className="w-5 h-5" />
                        Previous
                      </button>
                    )}

                    <button
                      onClick={handleNext}
                      className="px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-lg transition flex items-center gap-2 font-medium"
                    >
                      {currentStep === ONBOARDING_STEPS.length - 1 ? (
                        <>
                          <Check className="w-5 h-5" />
                          Finish
                        </>
                      ) : (
                        <>
                          {step.action}
                          <ChevronRight className="w-5 h-5" />
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <div className="text-center py-8">
                <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Check className="w-10 h-10 text-green-600" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">
                  You're All Set! 🎉
                </h3>
                <p className="text-gray-600">
                  Ready to start automated trading
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* CSS for highlights */}
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }

        .animate-slideUp {
          animation: slideUp 0.4s ease-out;
        }

        .onboarding-highlight {
          position: relative;
          z-index: 51;
          box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.5),
                      0 0 0 8px rgba(59, 130, 246, 0.2);
          border-radius: 8px;
          animation: pulse 2s infinite;
        }

        @keyframes pulse {
          0%, 100% {
            box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.5),
                        0 0 0 8px rgba(59, 130, 246, 0.2);
          }
          50% {
            box-shadow: 0 0 0 6px rgba(59, 130, 246, 0.6),
                        0 0 0 12px rgba(59, 130, 246, 0.3);
          }
        }
      `}</style>
    </>
  );
};

// Replay button component for Settings
export const OnboardingReplayButton = ({ onClick }) => {
  const handleReplay = () => {
    localStorage.removeItem('onboarding_completed');
    window.location.reload(); // or trigger onboarding directly
  };

  return (
    <button
      onClick={handleReplay}
      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition flex items-center gap-2"
    >
      <Zap className="w-4 h-4" />
      Replay Tutorial
    </button>
  );
};

export default Onboarding;
