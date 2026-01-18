"""Configuration file for CryptoTradeBot Pro - Complete Version"""

import os
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
LOGS_DIR = BASE_DIR / 'logs'

for directory in [DATA_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

EXCHANGE_CONFIG = {
    'name': 'binance',
    'api_key': os.getenv('EXCHANGE_API_KEY', ''),
    'api_secret': os.getenv('EXCHANGE_API_SECRET', ''),
    'testnet': True,
    'enable_rate_limit': True,
    'options': {'defaultType': 'spot'}
}

TRADING_PAIRS = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT']
PRIMARY_PAIR = 'BTC/USDT'

RISK_CONFIG = {
    'max_position_size_pct': 10.0,
    'max_total_exposure_pct': 50.0,
    'max_daily_loss_pct': 5.0,
    'max_drawdown_pct': 15.0,
    'stop_loss_pct': 2.0,
    'take_profit_pct': 5.0,
    'risk_per_trade_pct': 1.0,
    'max_open_positions': 5,
    'correlation_threshold': 0.7,
    'volatility_adjustment': True
}

GRID_STRATEGY_CONFIG = {
    'enabled': True,
    'symbol': PRIMARY_PAIR,
    'grid_levels': 10,
    'grid_spacing_pct': 1.0,
    'upper_price': None,
    'lower_price': None,
    'initial_capital': 1000,
    'rebalance_threshold': 5.0,
    'mode': 'auto',
    'leverage': 3,
    'risk_per_trade_percent': 2.0,
    'stop_loss_pct': 15.0,
    'tp_percentages': [1.0, 2.0, 3.0, 5.0, 8.0],
    'tp_position_pct': 20.0
}

STRATEGY_SELECTOR_CONFIG = {
    'enabled': True,
    'evaluation_period_days': 7,
    'min_trades_required': 10,
    'performance_weight': 0.5,
    'market_condition_weight': 0.3,
    'risk_weight': 0.2
}

EMAIL_CONFIG = {
    'enabled': False,
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': os.getenv('EMAIL_SENDER', ''),
    'sender_password': os.getenv('EMAIL_PASSWORD', ''),
    'recipient_email': os.getenv('EMAIL_RECIPIENT', ''),
    'notifications': {
        'trade_executed': True,
        'daily_report': True,
        'error_alerts': True,
        'stop_loss_triggered': True,
        'take_profit_triggered': True,
        'risk_limit_reached': True
    }
}

LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': str(LOGS_DIR / 'trading_bot.log'),
    'max_bytes': 10485760,
    'backup_count': 5,
    'console_output': True
}

DATABASE_CONFIG = {
    'type': 'sqlite',
    'path': str(DATA_DIR / 'trading_bot.db')
}

MARKET_DATA_CONFIG = {
    'timeframe': '1h',
    'lookback_candles': 100,
    'update_interval_seconds': 60
}

FEATURES = {
    'auto_strategy_selection': True,
    'risk_management': True,
    'email_notifications': EMAIL_CONFIG['enabled'],
    'paper_trading': True,
    'live_trading': False,
    'backtesting': True
}

def get_strategy_config(strategy_name: str) -> Dict:
    """Get configuration for specific strategy."""
    configs = {'grid': GRID_STRATEGY_CONFIG}
    return configs.get(strategy_name, {})

def get_active_strategies() -> List[str]:
    """Get list of enabled strategies."""
    strategies = []
    if GRID_STRATEGY_CONFIG['enabled']:
        strategies.append('grid')
    return strategies

def validate_config() -> bool:
    """Validate configuration settings."""
    if not EXCHANGE_CONFIG['api_key'] and not FEATURES['paper_trading']:
        print("⚠️ Warning: API key not configured!")
        return False
    
    if RISK_CONFIG['max_position_size_pct'] > RISK_CONFIG['max_total_exposure_pct']:
        print("⚠️ Warning: Position size larger than total exposure!")
        return False
        
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("CryptoTradeBot Pro - Configuration")
    print("=" * 60)
    
    if validate_config():
        print("✅ Configuration validated!")
        print(f"📊 Active strategies: {', '.join(get_active_strategies())}")
        print(f"🎯 Primary pair: {PRIMARY_PAIR}")
        print(f"🔒 Paper trading: {FEATURES['paper_trading']}")
    else:
        print("❌ Configuration validation failed!")
