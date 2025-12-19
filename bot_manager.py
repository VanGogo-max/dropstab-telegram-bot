# bot_manager.py - Central Bot Management System
import asyncio
from typing import Dict, List
import logging
from exchange_api import ExchangeAPI, MultiExchangeManager
from risk_manager import RiskManager
from dca_bot import DCABot
from signal_bot import SignalBot
from portfolio_bot import PortfolioBot
from trailing_bot import TrailingStopBot, MultiTrailingStopManager
from arbitrage_bot import ArbitrageBot

logger = logging.getLogger(__name__)

class BotManager:
    """
    Central controller for all trading bots
    - Start/stop individual bots
    - Monitor performance
    - Coordinate between bots
    """
    
    def __init__(self, user_id: str, config: Dict):
        self.user_id = user_id
        self.config = config
        
        # Initialize components
        self.exchange_manager = MultiExchangeManager()
        self.risk_manager = RiskManager(config.get('risk', {}))
        
        # Bots dictionary
        self.bots = {}
        self.bot_status = {}
        
        # Performance tracking
        self.total_pnl = 0
        self.active_bots_count = 0
    
    def add_exchange(self, name: str, api_key: str, api_secret: str, testnet: bool = False):
        """Add exchange connection"""
        self.exchange_manager.add_exchange(name, api_key, api_secret, testnet)
        logger.info(f"Exchange {name} added for user {self.user_id}")
    
    async def start_dca_bot(self, config: Dict) -> str:
        """Start DCA bot"""
        bot_id = f"dca_{config.get('symbol', 'BTC').replace('/', '_')}"
        
        exchange = self.exchange_manager.get_exchange(config.get('exchange', 'binance'))
        if not exchange:
            return "Exchange not configured"
        
        bot = DCABot(exchange, self.risk_manager, config)
        self.bots[bot_id] = bot
        
        asyncio.create_task(bot.start())
        self.bot_status[bot_id] = 'running'
        self.active_bots_count += 1
        
        logger.info(f"DCA bot started: {bot_id}")
        return bot_id
    
    async def start_signal_bot(self, config: Dict) -> str:
        """Start Signal bot"""
        bot_id = "signal_bot"
        
        exchange = self.exchange_manager.get_exchange(config.get('exchange', 'binance'))
        if not exchange:
            return "Exchange not configured"
        
        bot = SignalBot(exchange, self.risk_manager, config)
        self.bots[bot_id] = bot
        
        asyncio.create_task(bot.start())
        self.bot_status[bot_id] = 'running'
        self.active_bots_count += 1
        
        logger.info(f"Signal bot started: {bot_id}")
        return bot_id
    
    async def start_portfolio_bot(self, config: Dict) -> str:
        """Start Portfolio bot"""
        bot_id = "portfolio_bot"
        
        exchange = self.exchange_manager.get_exchange(config.get('exchange', 'binance'))
        if not exchange:
            return "Exchange not configured"
        
        bot = PortfolioBot(exchange, self.risk_manager, config)
        self.bots[bot_id] = bot
        
        asyncio.create_task(bot.start())
        self.bot_status[bot_id] = 'running'
        self.active_bots_count += 1
        
        logger.info(f"Portfolio bot started: {bot_id}")
        return bot_id
    
    async def start_trailing_bot(self, symbol: str, entry_price: float, 
                                amount: float, config: Dict) -> str:
        """Start Trailing Stop bot"""
        bot_id = f"trailing_{symbol.replace('/', '_')}"
        
        exchange = self.exchange_manager.get_exchange(config.get('exchange', 'binance'))
        if not exchange:
            return "Exchange not configured"
        
        bot = TrailingStopBot(exchange, self.risk_manager, config)
        await bot.start(entry_price, amount)
        
        self.bots[bot_id] = bot
        self.bot_status[bot_id] = 'running'
        self.active_bots_count += 1
        
        logger.info(f"Trailing bot started: {bot_id}")
        return bot_id
    
    async def start_arbitrage_bot(self, config: Dict) -> str:
        """Start Arbitrage bot"""
        bot_id = "arbitrage_bot"
        
        # Need at least 2 exchanges
        if len(self.exchange_manager.exchanges) < 2:
            return "Need at least 2 exchanges for arbitrage"
        
        bot = ArbitrageBot(self.exchange_manager.exchanges, self.risk_manager, config)
        self.bots[bot_id] = bot
        
        asyncio.create_task(bot.start())
        self.bot_status[bot_id] = 'running'
        self.active_bots_count += 1
        
        logger.info(f"Arbitrage bot started: {bot_id}")
        return bot_id
    
    def stop_bot(self, bot_id: str):
        """Stop specific bot"""
        if bot_id in self.bots:
            self.bots[bot_id].stop()
            self.bot_status[bot_id] = 'stopped'
            self.active_bots_count -= 1
            logger.info(f"Bot stopped: {bot_id}")
            return True
        return False
    
    def stop_all_bots(self):
        """Emergency stop all bots"""
        for bot_id in list(self.bots.keys()):
            self.stop_bot(bot_id)
        logger.warning(f"All bots stopped for user {self.user_id}")
    
    def get_bot_status(self, bot_id: str) -> Dict:
        """Get status of specific bot"""
        if bot_id not in self.bots:
            return {'error': 'Bot not found'}
        
        return self.bots[bot_id].get_status()
    
    def get_all_bots_status(self) -> Dict:
        """Get status of all bots"""
        status = {}
        for bot_id, bot in self.bots.items():
            status[bot_id] = {
                'status': self.bot_status.get(bot_id, 'unknown'),
                'details': bot.get_status()
            }
        return status
    
    async def get_total_performance(self) -> Dict:
        """Get combined performance of all bots"""
        total_profit = 0
        total_trades = 0
        
        for bot in self.bots.values():
            if hasattr(bot, 'get_performance'):
                perf = bot.get_performance()
                total_profit += perf.get('total_profit', 0)
                total_trades += perf.get('total_trades', 0)
        
        # Get current balances
        balances = await self.exchange_manager.get_all_balances()
        
        return {
            'user_id': self.user_id,
            'active_bots': self.active_bots_count,
            'total_profit': total_profit,
            'total_trades': total_trades,
            'balances': balances,
            'risk_status': self.risk_manager.get_status()
        }
    
    def get_dashboard_data(self) -> Dict:
        """Get data for user dashboard"""
        return {
            'user_id': self.user_id,
            'active_bots': self.active_bots_count,
            'bot_list': list(self.bots.keys()),
            'bot_statuses': self.bot_status,
            'risk_level': self.risk_manager.get_status(),
            'emergency_stop': self.risk_manager.emergency_stop
        }
