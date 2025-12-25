"""
Bot Manager - Central Controller
Manages: Spot (KCEX), Futures (Hyperliquid), Arbitrage (Multi-exchange)
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import threading
import time

from database import db_session, BotStatus, User
from risk_manager import risk_manager
from email_service import email_service
from config import *

# Import all bots
from dca_bot import DCABot
from signal_bot import SignalBot
from portfolio_bot import PortfolioBot
from trailing_bot import TrailingBot
from arbitrage_bot import ArbitrageBot
from futures_bot import FuturesBot
from grid_bot import GridBot
from aggressive_scalper_bot import AggressiveScalperBot
from trend_master_bot import TrendMasterBot
from mean_reversion_bot import MeanReversionBot
from dex_arbitrage_bot import DexArbitrageBot

logger = logging.getLogger(__name__)


class BotManager:
    """Central bot management system"""
    
    def __init__(self):
        self.active_bots: Dict[str, Dict] = {}
        self.bot_threads: Dict[str, threading.Thread] = {}
        self.running = False
        
        # Bot categories
        self.spot_bots = SPOT_BOTS  # ['dca', 'signal', 'portfolio', 'trailing', 'grid']
        self.futures_bots = FUTURES_BOTS  # ['futures']
        self.arbitrage_bots = ARBITRAGE_BOTS  # ['arbitrage']
        self.advanced_bots = ADVANCED_BOTS  # ['aggressive_scalper', 'trend_master', 'mean_reversion']
        
        logger.info("Bot Manager initialized")
    
    def create_bot_instance(self, user_id: int, bot_type: str, 
                           config: Dict) -> Optional[object]:
        """Create bot instance based on type"""
        try:
            # SPOT BOTS (KCEX)
            if bot_type == 'dca':
                return DCABot(
                    user_id=user_id,
                    symbol=config.get('symbol', 'BTC/USDT'),
                    amount=config.get('amount', DCA_AMOUNT),
                    interval_hours=config.get('interval', DCA_INTERVAL)
                )
            
            elif bot_type == 'signal':
                return SignalBot(
                    user_id=user_id,
                    symbol=config.get('symbol', 'BTC/USDT'),
                    indicators=config.get('indicators', ['RSI', 'MACD']),
                    position_size=config.get('position_size', 100)
                )
            
            elif bot_type == 'portfolio':
                return PortfolioBot(
                    user_id=user_id,
                    target_allocation=config.get('allocation', {
                        'BTC/USDT': 0.4,
                        'ETH/USDT': 0.3,
                        'SOL/USDT': 0.3
                    })
                )
            
            elif bot_type == 'trailing':
                return TrailingBot(
                    user_id=user_id,
                    symbol=config.get('symbol', 'BTC/USDT'),
                    trailing_percent=config.get('trailing_percent', TRAILING_STOP_PERCENT)
                )
            
            elif bot_type == 'grid':
                return GridBot(
                    user_id=user_id,
                    symbol=config.get('symbol', 'BTC/USDT'),
                    upper_price=config.get('upper_price', GRID_UPPER_PRICE),
                    lower_price=config.get('lower_price', GRID_LOWER_PRICE),
                    grids=config.get('grids', GRID_GRIDS),
                    amount_per_grid=config.get('amount_per_grid', GRID_AMOUNT_PER_GRID)
                )
            
            # FUTURES BOTS (Hyperliquid/Arbitrum)
            elif bot_type == 'futures':
                return FuturesBot(
                    user_id=user_id,
                    symbol=config.get('symbol', 'BTC/USDT')
                )
            
            # ARBITRAGE BOTS (DEX Spot-Futures)
            elif bot_type == 'dex_arbitrage':
                return DexArbitrageBot(
                    user_id=user_id,
                    symbol=config.get('symbol', 'BTC'),
                    capital=config.get('capital', 1000)
                )
            
            # Legacy CEX Arbitrage (deprecated but kept for compatibility)
            elif bot_type == 'arbitrage':
                return ArbitrageBot(
                    user_id=user_id,
                    exchanges=config.get('exchanges', ['kcex', 'binance']),
                    min_profit=config.get('min_profit', 0.005)
                )
            
            # ADVANCED STRATEGY BOTS
            elif bot_type == 'aggressive_scalper':
                return AggressiveScalperBot(
                    user_id=user_id,
                    symbol=config.get('symbol', 'BTC/USDT'),
                    risk_usd=config.get('risk_usd', SCALPER_RISK_USD),
                    max_leverage=config.get('max_leverage', SCALPER_MAX_LEVERAGE)
                )
            
            elif bot_type == 'trend_master':
                return TrendMasterBot(
                    user_id=user_id,
                    symbol=config.get('symbol', 'BTC/USDT'),
                    risk_usd=config.get('risk_usd', TREND_RISK_USD),
                    leverage=config.get('leverage', TREND_LEVERAGE)
                )
            
            elif bot_type == 'mean_reversion':
                return MeanReversionBot(
                    user_id=user_id,
                    symbol=config.get('symbol', 'BTC/USDT'),
                    risk_usd=config.get('risk_usd', MEANREV_RISK_USD),
                    leverage=config.get('leverage', MEANREV_LEVERAGE)
                )
            
            else:
                logger.error(f"Unknown bot type: {bot_type}")
                return None
                
        except Exception as e:
            logger.error(f"Bot creation error: {e}")
            return None
    
    def start_bot(self, user_id: int, bot_type: str, config: Dict) -> bool:
        """Start bot for user"""
        bot_key = f"{user_id}_{bot_type}"
        
        # Check if bot already running
        if bot_key in self.active_bots:
            logger.warning(f"Bot already running: {bot_key}")
            return False
        
        # Validate user subscription
        user = db_session.query(User).filter_by(id=user_id).first()
        if not user or not user.is_active_subscription():
            logger.warning(f"Invalid subscription: user {user_id}")
            return False
        
        # Check risk limits
        if not risk_manager.can_open_position(user_id):
            logger.warning(f"Risk limits exceeded: user {user_id}")
            return False
        
        # Create bot instance
        bot = self.create_bot_instance(user_id, bot_type, config)
        if not bot:
            return False
        
        # Store bot info
        self.active_bots[bot_key] = {
            'bot': bot,
            'user_id': user_id,
            'type': bot_type,
            'config': config,
            'started_at': datetime.utcnow(),
            'status': 'running'
        }
        
        # Start bot thread
        thread = threading.Thread(
            target=self._run_bot_loop,
            args=(bot_key,),
            daemon=True
        )
        thread.start()
        self.bot_threads[bot_key] = thread
        
        # Update database
        self._update_bot_status(user_id, bot_type, 'running', config)
        
        # Send notification
        exchange = self._get_bot_exchange(bot_type)
        email_service.send_bot_started(user_id, bot_type, exchange)
        
        logger.info(f"Bot started: {bot_key} on {exchange}")
        return True
    
    def stop_bot(self, user_id: int, bot_type: str) -> bool:
        """Stop bot for user"""
        bot_key = f"{user_id}_{bot_type}"
        
        if bot_key not in self.active_bots:
            logger.warning(f"Bot not running: {bot_key}")
            return False
        
        # Mark as stopping
        self.active_bots[bot_key]['status'] = 'stopping'
        
        # Wait for thread to finish (max 10 seconds)
        if bot_key in self.bot_threads:
            thread = self.bot_threads[bot_key]
            thread.join(timeout=10)
            del self.bot_threads[bot_key]
        
        # Remove from active bots
        del self.active_bots[bot_key]
        
        # Update database
        self._update_bot_status(user_id, bot_type, 'stopped', {})
        
        logger.info(f"Bot stopped: {bot_key}")
        return True
    
    def _run_bot_loop(self, bot_key: str):
        """Main bot execution loop"""
        try:
            bot_info = self.active_bots[bot_key]
            bot = bot_info['bot']
            bot_type = bot_info['type']
            
            # Determine run interval based on bot type
            if bot_type == 'futures':
                interval = 60  # 1 minute for futures
            elif bot_type == 'arbitrage':
                interval = 10  # 10 seconds for arbitrage
            else:
                interval = 300  # 5 minutes for spot
            
            while bot_info['status'] == 'running':
                try:
                    # Run bot logic
                    bot.run()
                    
                    # Update last run time
                    self._update_bot_status(
                        bot_info['user_id'],
                        bot_type,
                        'running',
                        bot_info['config']
                    )
                    
                except Exception as e:
                    logger.error(f"Bot execution error ({bot_key}): {e}")
                    
                    # Send alert
                    email_service.send_error_alert(
                        bot_info['user_id'],
                        f"Bot Error: {bot_type}",
                        str(e)
                    )
                
                # Sleep until next run
                time.sleep(interval)
                
        except Exception as e:
            logger.error(f"Bot loop error ({bot_key}): {e}")
        
        finally:
            logger.info(f"Bot loop ended: {bot_key}")
    
    def get_active_bots(self, user_id: int) -> List[Dict]:
        """Get all active bots for user"""
        user_bots = []
        
        for bot_key, bot_info in self.active_bots.items():
            if bot_info['user_id'] == user_id:
                user_bots.append({
                    'type': bot_info['type'],
                    'exchange': self._get_bot_exchange(bot_info['type']),
                    'status': bot_info['status'],
                    'started_at': bot_info['started_at'],
                    'config': bot_info['config']
                })
        
        return user_bots
    
    def get_bot_stats(self, user_id: int, bot_type: str) -> Dict:
        """Get bot performance statistics"""
        try:
            from database import Trade
            
            trades = db_session.query(Trade).filter_by(
                user_id=user_id,
                bot_type=bot_type
            ).all()
            
            total_trades = len(trades)
            winning_trades = sum(1 for t in trades if t.profit_loss > 0)
            total_profit = sum(t.profit_loss for t in trades if t.profit_loss)
            
            return {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'win_rate': winning_trades / total_trades if total_trades > 0 else 0,
                'total_profit': total_profit,
                'exchange': self._get_bot_exchange(bot_type)
            }
            
        except Exception as e:
            logger.error(f"Stats error: {e}")
            return {}
    
    def _get_bot_exchange(self, bot_type: str) -> str:
        """Get exchange name for bot type"""
        if bot_type in self.spot_bots:
            return 'KCEX (Spot)'
        elif bot_type in self.futures_bots:
            return 'Hyperliquid (Arbitrum Futures)'
        elif bot_type == 'dex_arbitrage':
            return 'Uniswap V3 + Hyperliquid (DEX)'
        elif bot_type == 'arbitrage':
            return 'Multi-Exchange (Legacy)'
        elif bot_type == 'aggressive_scalper':
            return 'Hyperliquid (Arbitrum Scalping)'
        elif bot_type in ['trend_master', 'mean_reversion']:
            return 'KCEX (Spot)'
        else:
            return 'Unknown'
    
    def _update_bot_status(self, user_id: int, bot_type: str, 
                          status: str, config: Dict):
        """Update bot status in database"""
        try:
            bot_status = db_session.query(BotStatus).filter_by(
                user_id=user_id,
                bot_type=bot_type
            ).first()
            
            if not bot_status:
                bot_status = BotStatus(
                    user_id=user_id,
                    bot_type=bot_type
                )
                db_session.add(bot_status)
            
            bot_status.status = status
            bot_status.config = config
            bot_status.last_run = datetime.utcnow()
            
            db_session.commit()
            
        except Exception as e:
            logger.error(f"Status update error: {e}")
            db_session.rollback()
    
    def stop_all_bots(self, user_id: Optional[int] = None):
        """Stop all bots (optionally for specific user)"""
        bots_to_stop = []
        
        for bot_key, bot_info in self.active_bots.items():
            if user_id is None or bot_info['user_id'] == user_id:
                bots_to_stop.append(
                    (bot_info['user_id'], bot_info['type'])
                )
        
        for uid, bot_type in bots_to_stop:
            self.stop_bot(uid, bot_type)
        
        logger.info(f"Stopped {len(bots_to_stop)} bots")
    
    def health_check(self) -> Dict:
        """Check health of all active bots"""
        health = {
            'total_bots': len(self.active_bots),
            'spot_bots': 0,
            'futures_bots': 0,
            'arbitrage_bots': 0,
            'exchanges': {
                'kcex': True,
                'hyperliquid': True
            }
        }
        
        for bot_info in self.active_bots.values():
            bot_type = bot_info['type']
            if bot_type in self.spot_bots:
                health['spot_bots'] += 1
            elif bot_type in self.futures_bots:
                health['futures_bots'] += 1
            elif bot_type in self.arbitrage_bots:
                health['arbitrage_bots'] += 1
        
        return health


# Global instance
bot_manager = BotManager()
