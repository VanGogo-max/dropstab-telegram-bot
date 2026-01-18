"""CryptoTradeBot Pro - Main Entry Point"""

import sys
import logging
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import (
    LOGGING_CONFIG,
    FEATURES,
    validate_config,
    get_active_strategies
)
from strategies.risk_manager import RiskManager
from strategies.strategy_auto_selector import StrategyAutoSelector
from strategies.advanced_grid_bot import AdvancedGridBot
from services.email_service import EmailService


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
        
        if not validate_config():
            self.logger.error("❌ Configuration validation failed!")
            sys.exit(1)
            
        self.risk_manager = None
        self.strategy_selector = None
        self.email_service = None
        
        self._initialize_components()
        
    def _initialize_components(self):
        """Initialize all bot components."""
        
        if FEATURES['email_notifications']:
            from config import EMAIL_CONFIG
            self.email_service = EmailService(EMAIL_CONFIG)
            self.logger.info("✅ Email service initialized")
        
        if FEATURES['risk_management']:
            from config import RISK_CONFIG
            self.risk_manager = RiskManager(RISK_CONFIG)
            self.logger.info("✅ Risk Manager initialized")
        
        if FEATURES['auto_strategy_selection']:
            self.strategy_selector = StrategyAutoSelector()
            
            from config import GRID_STRATEGY_CONFIG
            grid_strategy = AdvancedGridBot(GRID_STRATEGY_CONFIG)
            self.strategy_selector.register_strategy(grid_strategy)
            
            self.logger.info("✅ Strategy Auto Selector initialized")
            self.logger.info(f"📊 Active strategies: {', '.join(get_active_strategies())}")
    
    def start(self):
        """Start the trading bot."""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("🎯 Bot Started Successfully!")
        self.logger.info("=" * 60)
        
        self._show_configuration()
        
        if self.email_service:
            self.email_service.send_alert(
                'info',
                f'CryptoTradeBot Pro started at {datetime.now()}',
                'normal'
            )
        
        try:
            self._run_trading_loop()
        except KeyboardInterrupt:
            self.logger.info("\n⚠️ Shutting down gracefully...")
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
            self.logger.warning("📝 PAPER TRADING MODE - No real trades!")
        
        import time
        
        self.logger.info("✅ Bot is running. Press Ctrl+C to stop.")
        
        while True:
            try:
                time.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Error in trading loop: {e}")
                time.sleep(10)
    
    def stop(self):
        """Stop the trading bot."""
        self.logger.info("🛑 Stopping bot...")
        
        if self.email_service:
            self.email_service.send_alert(
                'info',
                f'CryptoTradeBot Pro stopped at {datetime.now()}',
                'normal'
            )
        
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
