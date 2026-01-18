"""
CryptoTradeBot Pro - Main Entry Point
Starts the trading bot with all strategies and risk management
"""

import sys
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    LOGGING_CONFIG,
    FEATURES,
    validate_config,
    get_active_strategies
)
from strategies.risk_manager import RiskManager
from strategies.strategy_auto_selector import StrategyAutoSelector
from strategies.grid_bot import GridTradingStrategy
from services.email_service import EmailService

# Import existing files
try:
    from database import Database
except ImportError:
    Database = None
    
try:
    from exchange_apy import ExchangeAPI  # или exchange_api
except ImportError:
    ExchangeAPI = None


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, LOGGING_CONFIG['level']),
        format=LOGGING_CONFIG['format'],
        handlers=[
            logging.FileHandler(LOGGING_CONFIG['file']),
            logging.StreamHandler() if LOGGING_CONFIG['console_output'] else logging.NullHandler()
        ]
    )
    return logging.getLogger(__name__)


class TradingBot:
    """Main Trading Bot Controller."""
    
    def __init__(self):
        """Initialize trading bot."""
        self.logger = setup_logging()
        self.logger.info("=" * 60)
        self.logger.info("🚀 CryptoTradeBot Pro Starting...")
        self.logger.info("=" * 60)
        
        # Validate configuration
        if not validate_config():
            self.logger.error("❌ Configuration validation failed!")
            sys.exit(1)
            
        # Initialize components
        self.risk_manager = None
        self.strategy_selector = None
        self.email_service = None
        self.exchange = None
        self.database = None
        
        self._initialize_components()
        
    def _initialize_components(self):
        """Initialize all bot components."""
        
        # 1. Email Service
        if FEATURES['email_notifications']:
            from config import EMAIL_CONFIG
            self.email_service = EmailService(EMAIL_CONFIG)
            self.logger.info("✅ Email service initialized")
        
        # 2. Database (if exists)
        if Database:
            try:
                self.database = Database()
                self.logger.info("✅ Database connected")
            except Exception as e:
                self.logger.error(f"❌ Database connection failed: {e}")
        
        # 3. Exchange API (if exists)
        if ExchangeAPI:
            try:
                from config import EXCHANGE_CONFIG
                self.exchange = ExchangeAPI(EXCHANGE_CONFIG)
                self.logger.info("✅ Exchange API connected")
            except Exception as e:
                self.logger.error(f"❌ Exchange connection failed: {e}")
        
        # 4. Risk Manager
        if FEATURES['risk_management']:
            from config import RISK_CONFIG
            self.risk_manager = RiskManager(RISK_CONFIG)
            self.logger.info("✅ Risk Manager initialized")
        
        # 5. Strategy Auto Selector
        if FEATURES['auto_strategy_selection']:
            self.strategy_selector = StrategyAutoSelector()
            
            # Register available strategies
            from config import GRID_STRATEGY_CONFIG
            grid_strategy = GridTradingStrategy(GRID_STRATEGY_CONFIG)
            self.strategy_selector.register_strategy(grid_strategy)
            
            self.logger.info("✅ Strategy Auto Selector initialized")
            self.logger.info(f"📊 Active strategies: {', '.join(get_active_strategies())}")
    
    def start(self):
        """Start the trading bot."""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("🎯 Bot Started Successfully!")
        self.logger.info("=" * 60)
        
        # Show configuration
        self._show_configuration()
        
        # Send startup notification
        if self.email_service:
            self.email_service.send_alert(
                'info',
                f'CryptoTradeBot Pro started successfully at {datetime.now()}',
                'normal'
            )
        
        # Start main trading loop
        try:
            self._run_trading_loop()
        except KeyboardInterrupt:
            self.logger.info("\n⚠️  Shutting down gracefully...")
            self.stop()
        except Exception as e:
            self.logger.error(f"❌ Critical error: {e}", exc_info=True)
            self.stop()
    
    def _show_configuration(self):
        """Display current configuration."""
        from config import PRIMARY_PAIR, FEATURES
        
        print("\n📋 Current Configuration:")
        print(f"   Primary Pair: {PRIMARY_PAIR}")
        print(f"   Paper Trading: {FEATURES['paper_trading']}")
        print(f"   Live Trading: {FEATURES['live_trading']}")
        print(f"   Risk Management: {FEATURES['risk_management']}")
        print(f"   Auto Strategy Selection: {FEATURES['auto_strategy_selection']}")
        print(f"   Email Notifications: {FEATURES['email_notifications']}")
        print()
    
    def _run_trading_loop(self):
        """Main trading loop."""
        self.logger.info("🔄 Starting trading loop...")
        
        if FEATURES['paper_trading']:
            self.logger.warning("📝 PAPER TRADING MODE - No real trades will be executed!")
        
        # This is where the main logic runs
        # For now, just keep alive
        import time
        
        self.logger.info("✅ Bot is running. Press Ctrl+C to stop.")
        
        while True:
            try:
                # TODO: Add your trading logic here
                # Example:
                # 1. Fetch market data
                # 2. Run strategy analysis
                # 3. Check risk limits
                # 4. Execute trades
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in trading loop: {e}")
                time.sleep(10)
    
    def stop(self):
        """Stop the trading bot."""
        self.logger.info("🛑 Stopping bot...")
        
        # Send shutdown notification
        if self.email_service:
            self.email_service.send_alert(
                'info',
                f'CryptoTradeBot Pro stopped at {datetime.now()}',
                'normal'
            )
        
        # Close database connection
        if self.database:
            try:
                self.database.close()
                self.logger.info("✅ Database connection closed")
            except:
                pass
        
        self.logger.info("👋 Bot stopped successfully!")
        sys.exit(0)


def main():
    """Main entry point."""
    try:
        bot = TradingBot()
        bot.start()
    except Exception as e:
        logging.error(f"Failed to start bot: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
