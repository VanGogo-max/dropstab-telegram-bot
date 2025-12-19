# config.py - Main Configuration
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Main application configuration"""
    
    # Application
    APP_NAME = "CryptoTradeBot Pro"
    VERSION = "1.0.0"
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost/cryptobot')
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')  # Change this!
    JWT_ALGORITHM = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
    
    # Payments
    PAYMENT_ADDRESS = '0xfee37e7e64d70f37f96c42375131abb57c1481c2'
    POLYGON_RPC = os.getenv('POLYGON_RPC', 'https://polygon-rpc.com')
    BASE_SUBSCRIPTION_PRICE = 39  # USD per month
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_ADMIN_ID = os.getenv('TELEGRAM_ADMIN_ID', '')
    
    # Risk Management (Conservative defaults)
    RISK_CONFIG = {
        'max_position_size': 0.10,  # 10% of balance
        'max_daily_loss': 0.05,  # 5% daily loss limit
        'max_drawdown': 0.10,  # 10% max drawdown
        'max_leverage': 3,  # Max 3x leverage
        'max_open_positions': 5,
        'min_profit_target': 0.02,  # 2%
        'stop_loss_percent': 0.03  # 3%
    }
    
    # DCA Bot Defaults
    DCA_CONFIG = {
        'interval_hours': 24,
        'amount_per_order': 50,
        'max_total_investment': 1000,
        'take_profit_percent': 0.15
    }
    
    # Signal Bot Defaults
    SIGNAL_CONFIG = {
        'timeframe': '1h',
        'auto_trade': False,
        'position_size': 0.05,
        'rsi_oversold': 30,
        'rsi_overbought': 70,
        'min_confirmations': 2
    }
    
    # Portfolio Bot Defaults
    PORTFOLIO_CONFIG = {
        'target_allocation': {
            'BTC/USDT': 0.50,
            'ETH/USDT': 0.30,
            'SOL/USDT': 0.20
        },
        'rebalance_threshold': 0.05,
        'rebalance_interval': 24,
        'min_trade_value': 20
    }
    
    # Trailing Stop Defaults
    TRAILING_CONFIG = {
        'trailing_percent': 0.03,
        'activation_profit': 0.05,
        'check_interval': 60
    }
    
    # Arbitrage Bot Defaults
    ARBITRAGE_CONFIG = {
        'min_profit': 0.005,  # 0.5%
        'max_position': 1000,
        'check_interval': 30
    }
    
    # Referral System
    REFERRAL_CONFIG = {
        'discount_per_referral': 0.20,  # 20%
        'free_threshold': 5,  # Free after 5 referrals
        'max_discount': 0.95  # Max 95% discount
    }
    
    # Exchanges (add your API keys)
    EXCHANGES = {
        'binance': {
            'api_key': os.getenv('BINANCE_API_KEY', ''),
            'api_secret': os.getenv('BINANCE_API_SECRET', ''),
            'testnet': os.getenv('BINANCE_TESTNET', 'True') == 'True'
        },
        'okx': {
            'api_key': os.getenv('OKX_API_KEY', ''),
            'api_secret': os.getenv('OKX_API_SECRET', ''),
            'testnet': os.getenv('OKX_TESTNET', 'True') == 'True'
        },
        'bybit': {
            'api_key': os.getenv('BYBIT_API_KEY', ''),
            'api_secret': os.getenv('BYBIT_API_SECRET', ''),
            'testnet': os.getenv('BYBIT_TESTNET', 'True') == 'True'
        }
    }
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = 'cryptobot.log'
    
    # Features
    FEATURES = {
        'dca_bot': True,
        'signal_bot': True,
        'portfolio_bot': True,
        'trailing_bot': True,
        'arbitrage_bot': True,
        'grid_bot': True,
        'futures_bot': True
    }
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        errors = []
        
        if not cls.SECRET_KEY or cls.SECRET_KEY == 'your-secret-key-change-this':
            errors.append("SECRET_KEY must be set")
        
        if cls.ADMIN_PASSWORD == 'admin123':
            errors.append("ADMIN_PASSWORD must be changed")
        
        if not cls.TELEGRAM_BOT_TOKEN:
            errors.append("TELEGRAM_BOT_TOKEN not set")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True

# Development config
class DevelopmentConfig(Config):
    DEBUG = True
    
# Production config  
class ProductionConfig(Config):
    DEBUG = False
    
# Get config based on environment
config = ProductionConfig if os.getenv('ENV') == 'production' else DevelopmentConfig
