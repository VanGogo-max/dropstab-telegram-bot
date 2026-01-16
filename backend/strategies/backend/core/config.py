"""
Configuration for CryptoTradeBot Pro
Spot: KCEX | Futures: Hyperliquid (Arbitrum)
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ==================== EXCHANGE CONFIGURATION ====================

# KCEX - Spot Trading (Primary)
KCEX_API_KEY = os.getenv('KCEX_API_KEY', '')
KCEX_API_SECRET = os.getenv('KCEX_API_SECRET', '')
KCEX_TESTNET = os.getenv('KCEX_TESTNET', 'true').lower() == 'true'

# Hyperliquid - Futures Trading (Arbitrum Network)
HYPERLIQUID_WALLET = os.getenv('HYPERLIQUID_WALLET', '0x...')
HYPERLIQUID_PRIVATE_KEY = os.getenv('HYPERLIQUID_PRIVATE_KEY', '')
HYPERLIQUID_TESTNET = os.getenv('HYPERLIQUID_TESTNET', 'true').lower() == 'true'
HYPERLIQUID_NETWORK = 'arbitrum'

# Legacy exchanges (for arbitrage bot only)
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
BINANCE_SECRET = os.getenv('BINANCE_SECRET', '')
OKX_API_KEY = os.getenv('OKX_API_KEY', '')
OKX_SECRET = os.getenv('OKX_SECRET', '')
OKX_PASSWORD = os.getenv('OKX_PASSWORD', '')

# ==================== TRADING CONFIGURATION ====================

# Risk Management
MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', '1000'))
MAX_DAILY_LOSS = float(os.getenv('MAX_DAILY_LOSS', '100'))
MAX_OPEN_POSITIONS = int(os.getenv('MAX_OPEN_POSITIONS', '3'))

# Futures Specific
FUTURES_MAX_LEVERAGE = int(os.getenv('FUTURES_MAX_LEVERAGE', '3'))
FUTURES_POSITION_RISK = float(os.getenv('FUTURES_POSITION_RISK', '0.02'))

# Spot Trading
SPOT_MIN_ORDER_SIZE = float(os.getenv('SPOT_MIN_ORDER_SIZE', '10'))

# ==================== PARTIAL TAKE PROFIT CONFIGURATION ====================

# Conservative Profile (Default)
TP_CONSERVATIVE = {
    'tp1': {'percentage': 62, 'ratio': 0.62},
    'tp2': {'percentage': 31, 'ratio': 0.31},
    'tp3': {'percentage': 8, 'ratio': 0.08}
}

# Balanced Profile
TP_BALANCED = {
    'tp1': {'percentage': 50, 'ratio': 0.50},
    'tp2': {'percentage': 30, 'ratio': 0.30},
    'tp3': {'percentage': 20, 'ratio': 0.20}
}

# Aggressive Profile
TP_AGGRESSIVE = {
    'tp1': {'percentage': 33, 'ratio': 0.33},
    'tp2': {'percentage': 33, 'ratio': 0.33},
    'tp3': {'percentage': 34, 'ratio': 0.34}
}

# Default TP Profile
DEFAULT_TP_PROFILE = os.getenv('DEFAULT_TP_PROFILE', 'conservative')

# TP Distance Multipliers (from entry)
TP1_MULTIPLIER = float(os.getenv('TP1_MULTIPLIER', '1.5'))  # 1.5x risk
TP2_MULTIPLIER = float(os.getenv('TP2_MULTIPLIER', '2.5'))  # 2.5x risk
TP3_MULTIPLIER = float(os.getenv('TP3_MULTIPLIER', '4.0'))  # 4x risk

# Trailing Stop for TP3
TP3_TRAILING_STOP = True
TP3_TRAILING_PERCENT = float(os.getenv('TP3_TRAILING_PERCENT', '0.5'))  # 0.5%

# ==================== BOT CONFIGURATION ====================

# Bot Categories
SPOT_BOTS = ['dca', 'signal', 'portfolio', 'trailing', 'grid']
FUTURES_BOTS = ['futures']
ARBITRAGE_BOTS = ['dex_arbitrage']
ADVANCED_BOTS = ['aggressive_scalper', 'trend_master', 'mean_reversion']

# DCA Bot
DCA_AMOUNT = float(os.getenv('DCA_AMOUNT', '50'))
DCA_INTERVAL = int(os.getenv('DCA_INTERVAL', '24'))

# Signal Bot
SIGNAL_RSI_OVERSOLD = int(os.getenv('SIGNAL_RSI_OVERSOLD', '30'))
SIGNAL_RSI_OVERBOUGHT = int(os.getenv('SIGNAL_RSI_OVERBOUGHT', '70'))

# Portfolio Bot
PORTFOLIO_REBALANCE_THRESHOLD = float(os.getenv('PORTFOLIO_REBALANCE_THRESHOLD', '0.05'))

# Trailing Stop Bot
TRAILING_STOP_PERCENT = float(os.getenv('TRAILING_STOP_PERCENT', '0.03'))

# Futures Bot (Turtle Strategy)
TURTLE_SYSTEM = int(os.getenv('TURTLE_SYSTEM', '2'))
TURTLE_BREAKOUT_PERIOD = int(os.getenv('TURTLE_BREAKOUT_PERIOD', '55'))
TURTLE_EXIT_PERIOD = int(os.getenv('TURTLE_EXIT_PERIOD', '10'))
TURTLE_ATR_PERIOD = int(os.getenv('TURTLE_ATR_PERIOD', '20'))
TURTLE_MAX_UNITS = int(os.getenv('TURTLE_MAX_UNITS', '4'))
TURTLE_UNIT_RISK = float(os.getenv('TURTLE_UNIT_RISK', '0.01'))

# Grid Bot (KCEX Spot)
GRID_UPPER_PRICE = float(os.getenv('GRID_UPPER_PRICE', '50000'))
GRID_LOWER_PRICE = float(os.getenv('GRID_LOWER_PRICE', '40000'))
GRID_GRIDS = int(os.getenv('GRID_GRIDS', '10'))
GRID_AMOUNT_PER_GRID = float(os.getenv('GRID_AMOUNT_PER_GRID', '50'))

# Aggressive Scalper Bot (Hyperliquid)
SCALPER_MAX_LEVERAGE = int(os.getenv('SCALPER_MAX_LEVERAGE', '20'))
SCALPER_RISK_USD = float(os.getenv('SCALPER_RISK_USD', '5'))
SCALPER_STOP_LOSS_PCT = float(os.getenv('SCALPER_STOP_LOSS_PCT', '0.003'))
SCALPER_TAKE_PROFIT_PCT = float(os.getenv('SCALPER_TAKE_PROFIT_PCT', '0.01'))

# Trend Master Bot (KCEX)
TREND_LEVERAGE = int(os.getenv('TREND_LEVERAGE', '5'))
TREND_RISK_USD = float(os.getenv('TREND_RISK_USD', '5'))
TREND_REWARD_RATIO = int(os.getenv('TREND_REWARD_RATIO', '2'))

# Mean Reversion Bot (KCEX)
MEANREV_LEVERAGE = int(os.getenv('MEANREV_LEVERAGE', '3'))
MEANREV_RISK_USD = float(os.getenv('MEANREV_RISK_USD', '5'))
MEANREV_BB_PERIOD = int(os.getenv('MEANREV_BB_PERIOD', '20'))
MEANREV_ADX_THRESHOLD = int(os.getenv('MEANREV_ADX_THRESHOLD', '25'))

# DEX Arbitrage Bot (Uniswap + Hyperliquid)
DEX_MIN_FUNDING_RATE = float(os.getenv('DEX_MIN_FUNDING_RATE', '0.005'))
DEX_MIN_BASIS_SPREAD = float(os.getenv('DEX_MIN_BASIS_SPREAD', '0.01'))
DEX_MAX_POSITIONS = int(os.getenv('DEX_MAX_POSITIONS', '2'))
DEX_POSITION_SIZE_PCT = float(os.getenv('DEX_POSITION_SIZE_PCT', '0.5'))

# ==================== DATABASE ====================

DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres:password@localhost:5432/cryptobot'
)

# ==================== PAYMENT & BUSINESS ====================

# USDT Payment (Polygon Network) - FIXED: Move to .env
USDT_WALLET_ADDRESS = os.getenv('USDT_WALLET_ADDRESS', '')
POLYGON_RPC_URL = os.getenv(
    'POLYGON_RPC_URL',
    'https://polygon-rpc.com'
)

# Pricing
SUBSCRIPTION_PRICE = 10
REFERRAL_DISCOUNT = 1.00
FREE_REFERRALS_NEEDED = 10

# ==================== NOTIFICATIONS ====================

# Email (SendGrid)
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '')
FROM_EMAIL = os.getenv('FROM_EMAIL', 'bot@cryptotradepro.com')

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_ADMIN_ID = os.getenv('TELEGRAM_ADMIN_ID', '')

# ==================== MONITORING ====================

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Alerts
ALERT_ON_TRADE = True
ALERT_ON_ERROR = True
ALERT_DAILY_REPORT = True

# ==================== SECURITY ====================

JWT_SECRET = os.getenv('JWT_SECRET', 'change-me-in-production')
JWT_EXPIRATION = 3600

API_RATE_LIMIT = int(os.getenv('API_RATE_LIMIT', '100'))

# ==================== SUPPORTED PAIRS ====================

# KCEX Spot Pairs
KCEX_SPOT_PAIRS = [
    'BTC/USDT', 'ETH/USDT', 'BNB/USDT',
    'SOL/USDT', 'XRP/USDT', 'ADA/USDT'
]

# Hyperliquid Futures Pairs (Arbitrum)
HYPERLIQUID_FUTURES_PAIRS = [
    'BTC/USDT', 'ETH/USDT', 'SOL/USDT',
    'ARB/USDT', 'AVAX/USDT'
]

# ==================== ENVIRONMENT ====================

ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
DEBUG = os.getenv('DEBUG', 'true').lower() == 'true'

# Testnet mode (safety first!)
GLOBAL_TESTNET = os.getenv('GLOBAL_TESTNET', 'true').lower() == 'true'

if GLOBAL_TESTNET:
    print("⚠️  TESTNET MODE ENABLED - No real money trades")


# ==================== CONFIG CLASS ====================

class Config:
    """Configuration object with validation"""
    
    def __init__(self):
        # Copy all uppercase variables as attributes
        for key, value in globals().items():
            if key.isupper() and not key.startswith('_'):
                setattr(self, key, value)
    
    @property
    def APP_NAME(self):
        return "CryptoTradeBot Pro"
    
    @property
    def VERSION(self):
        return "2.0.0"
    
    @property
    def LOG_FILE(self):
        return "bot.log"
    
    @property
    def ADMIN_PASSWORD(self):
        return os.getenv('ADMIN_PASSWORD', 'admin123')
    
    def validate(self):
        """Validate critical configuration"""
        errors = []
        
        # Check database
        if not self.DATABASE_URL:
            errors.append("DATABASE_URL not set")
        
        # Check if at least one exchange is configured
        has_exchange = (
            (self.KCEX_API_KEY and self.KCEX_API_SECRET) or
            (self.HYPERLIQUID_WALLET and self.HYPERLIQUID_PRIVATE_KEY)
        )
        
        if not has_exchange and not self.GLOBAL_TESTNET:
            errors.append("No exchange API keys configured")
        
        # Check payment wallet
        if not self.USDT_WALLET_ADDRESS and not self.GLOBAL_TESTNET:
            errors.append("USDT_WALLET_ADDRESS not set")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True
    
    def get_tp_profile(self, profile_name: str = None):
        """Get Take Profit profile"""
        if profile_name is None:
            profile_name = self.DEFAULT_TP_PROFILE
        
        profiles = {
            'conservative': TP_CONSERVATIVE,
            'balanced': TP_BALANCED,
            'aggressive': TP_AGGRESSIVE
        }
        
        return profiles.get(profile_name, TP_CONSERVATIVE)


# Global config instance
config = Config()
