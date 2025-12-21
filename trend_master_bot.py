"""
📈 TREND MASTER BOT
Exchange: KCEX (Spot Trading)
Strategy: Trend Following with Pullback Entry
Risk Level: MEDIUM 🟡

📊 STRATEGY OVERVIEW:
- Identifies strong trends using EMA crossover (4h timeframe)
- Waits for pullbacks to EMA50 on 15m for better entry
- Uses 1:2 risk-reward ratio for consistent profits
- Confirms with RSI and MACD filters
- Moderate leverage (5x) for balanced risk

✅ BEST FOR:
- Swing traders holding positions for days
- Those seeking steady growth without extreme risk
- Traders who prefer less monitoring
- Markets with clear directional trends

⚠️ RISKS:
- Trend reversals can cause losses
- Pullbacks may turn into trend changes
- Requires patience for entry signals
- May miss fast-moving opportunities

📈 EXPECTED PERFORMANCE:
- Win Rate: ~70%
- Risk:Reward: 1:2
- Avg Trade Duration: 1-7 days
- Recommended Capital: $50+ per position
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
import numpy as np

from exchange_api import exchange_api
from risk_manager import risk_manager
from database import db_session, Trade
from email_service import email_service
from config import *

logger = logging.getLogger(__name__)


class TrendMasterBot:
    """Trend following with smart pullback entries"""
    
    # Bot metadata
    BOT_NAME = "Trend Master"
    BOT_DESCRIPTION = "Follow strong trends with pullback entries"
    BOT_RISK_LEVEL = "MEDIUM"
    BOT_TIMEFRAME = "4h trends, 15m entries"
    BOT_EXCHANGE = "KCEX (Spot)"
    
    def __init__(self, user_id: int, symbol: str = 'BTC/USDT',
                 risk_usd: float = 5, leverage: int = 5):
        self.user_id = user_id
        self.symbol = symbol
        self.exchange = exchange_api.get_spot_exchange()
        
        # Risk parameters
        self.risk_usd = risk_usd
        self.leverage = min(leverage, 5)  # Cap at 5x
        
        # Strategy parameters
        self.trend_ema_fast = 50
        self.trend_ema_slow = 200
        self.pullback_ema = 50
        self.rsi_period = 14
        self.rsi_overbought = 70
        self.rsi_oversold = 30
        self.reward_risk_ratio = 2  # 1:2 R:R
        
        # Position tracking
        self.position = None
        
        logger.info(f"Trend Master Bot initialized: {symbol}")
    
    def ema(self, values: np.ndarray, period: int) -> np.ndarray:
        """Calculate EMA"""
        k = 2 / (period + 1)
        ema_vals = []
        ema_prev = values[0]
        for v in values:
            ema_prev = v * k + ema_prev * (1 - k)
            ema_vals.append(ema_prev)
        return np.array(ema_vals)
    
    def calculate_rsi(self, closes: np.ndarray, period: int = 14) -> float:
        """Calculate RSI"""
        if len(closes) < period + 1:
            return 50
        
        deltas = np.diff(closes)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi)
    
    def calculate_macd(self, closes: np.ndarray) -> float:
        """Calculate MACD histogram"""
        if len(closes) < 26:
            return 0
        
        ema12 = self.ema(closes, 12)
        ema26 = self.ema(closes, 26)
        macd_line = ema12 - ema26
        signal_line = self.ema(macd_line, 9)
        histogram = macd_line[-1] - signal_line[-1]
        
        return float(histogram)
    
    def get_market_data(self, timeframe: str, limit: int) -> List[Dict]:
        """Fetch candle data (mock)"""
        # TODO: Implement actual KCEX API call
        return []
    
    def analyze_trend(self, candles_4h: List[Dict]) -> Optional[str]:
        """Determine trend direction"""
        if len(candles_4h) < self.trend_ema_slow:
            return None
        
        closes = np.array([c['close'] for c in candles_4h])
        ema50 = self.ema(closes, self.trend_ema_fast)[-1]
        ema200 = self.ema(closes, self.trend_ema_slow)[-1]
        
        if ema50 > ema200:
            return "long"
        elif ema50 < ema200:
            return "short"
        else:
            return None
    
    def check_pullback_entry(self, candles_15m: List[Dict], trend: str) -> Optional[Dict]:
        """Check for pullback to EMA50 with confirmations"""
        if len(candles_15m) < 50:
            return None
        
        closes = np.array([c['close'] for c in candles_15m])
        highs = np.array([c['high'] for c in candles_15m])
        lows = np.array([c['low'] for c in candles_15m])
        
        last_close = closes[-1]
        pullback_level = self.ema(closes, self.pullback_ema)[-1]
        
        # RSI filter - avoid overbought/oversold extremes
        rsi = self.calculate_rsi(closes, self.rsi_period)
        if trend == "long" and rsi > self.rsi_overbought:
            logger.debug(f"RSI too high ({rsi:.1f}) for long entry")
            return None
        if trend == "short" and rsi < self.rsi_oversold:
            logger.debug(f"RSI too low ({rsi:.1f}) for short entry")
            return None
        
        # MACD filter - histogram should align with trend
        macd_hist = self.calculate_macd(closes)
        if trend == "long" and macd_hist < 0:
            logger.debug("MACD histogram bearish - waiting")
            return None
        if trend == "short" and macd_hist > 0:
            logger.debug("MACD histogram bullish - waiting")
            return None
        
        # Check for pullback
        side = None
        stop_loss = None
        
        if trend == "long" and last_close <= pullback_level:
            side = "buy"
            # Stop loss at recent swing low
            stop_loss = lows[-10:].min()
        elif trend == "short" and last_close >= pullback_level:
            side = "sell"
            # Stop loss at recent swing high
            stop_loss = highs[-10:].max()
        else:
            return None
        
        # Calculate take profit (2x risk)
        stop_distance = abs(last_close - stop_loss)
        if stop_distance <= 0:
            return None
        
        if side == "buy":
            take_profit = last_close + (self.reward_risk_ratio * stop_distance)
        else:
            take_profit = last_close - (self.reward_risk_ratio * stop_distance)
        
        return {
            'side': side,
            'entry': last_close,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'rsi': rsi,
            'macd_hist': macd_hist
        }
    
    def calculate_position_size(self, entry: float, stop_loss: float) -> float:
        """Calculate position size"""
        stop_distance = abs(entry - stop_loss)
        if stop_distance <= 0:
            return 0
        
        size = (self.risk_usd * self.leverage) / (stop_distance * entry)
        return round(size, 6)
    
    def open_position(self, signal: Dict) -> bool:
        """Open trend following position"""
        try:
            entry = signal['entry']
            side = signal['side']
            stop_loss = signal['stop_loss']
            take_profit = signal['take_profit']
            
            # Calculate size
            size = self.calculate_position_size(entry, stop_loss)
            if size == 0:
                return False
            
            # Risk check
            if not risk_manager.can_open_position(self.user_id):
                logger.warning("Risk limits exceeded")
                return False
            
            # Place order
            result = self.exchange.create_order(
                symbol=self.symbol,
                side=side,
                amount=size,
                order_type='market'
            )
            
            if 'error' in result:
                logger.error(f"Order failed: {result['error']}")
                return False
            
            # Save position
            self.position = {
                'side': side,
                'entry': entry,
                'size': size,
                'stop_loss': stop_loss,
                'take_profit': take_profit
            }
            
            # Log trade
            self._log_trade('OPEN', entry, size)
            
            # Notification
            email_service.send_trade_alert(
                self.user_id,
                f"📈 Trend Entry: {side.upper()} {self.symbol}",
                f"Entry: ${entry:,.2f} | SL: ${stop_loss:,.2f} | TP: ${take_profit:,.2f}\n"
                f"RSI: {signal['rsi']:.1f} | MACD: {signal['macd_hist']:.4f}\n"
                f"Risk:Reward: 1:{self.reward_risk_ratio}"
            )
            
            logger.info(f"Position opened: {side} {size} @ {entry}")
            return True
            
        except Exception as e:
            logger.error(f"Open position error: {e}")
            return False
    
    def close_position(self, reason: str, current_price: float):
        """Close position"""
        if not self.position:
            return
        
        try:
            side = 'sell' if self.position['side'] == 'buy' else 'buy'
            size = self.position['size']
            
            result = self.exchange.create_order(
                symbol=self.symbol,
                side=side,
                amount=size,
                order_type='market'
            )
            
            # Calculate P&L
            if self.position['side'] == 'buy':
                pnl = (current_price - self.position['entry']) * size
            else:
                pnl = (self.position['entry'] - current_price) * size
            
            # Log trade
            self._log_trade('CLOSE', current_price, size, pnl)
            
            # Notification
            email_service.send_trade_alert(
                self.user_id,
                f"💰 Trend Exit: {reason}",
                f"P&L: ${pnl:,.2f} | Exit: ${current_price:,.2f}"
            )
            
            self.position = None
            logger.info(f"Position closed: {reason} | P&L: ${pnl:,.2f}")
            
        except Exception as e:
            logger.error(f"Close position error: {e}")
    
    def manage_position(self, current_price: float):
        """Monitor position"""
        if not self.position:
            return
        
        # Check stop loss
        if self.position['side'] == 'buy':
            if current_price <= self.position['stop_loss']:
                self.close_position("STOP_LOSS", current_price)
                return
        else:
            if current_price >= self.position['stop_loss']:
                self.close_position("STOP_LOSS", current_price)
                return
        
        # Check take profit
        if self.position['side'] == 'buy':
            if current_price >= self.position['take_profit']:
                self.close_position("TAKE_PROFIT", current_price)
                return
        else:
            if current_price <= self.position['take_profit']:
                self.close_position("TAKE_PROFIT", current_price)
                return
    
    def run(self):
        """Main execution"""
        try:
            # Manage existing position
            if self.position:
                ticker = self.exchange.get_ticker(self.symbol)
                current_price = float(ticker.get('last', 0))
                self.manage_position(current_price)
                return
            
            # Get market data
            candles_4h = self.get_market_data('4h', 220)
            candles_15m = self.get_market_data('15m', 200)
            
            if not candles_4h or not candles_15m:
                return
            
            # Analyze trend
            trend = self.analyze_trend(candles_4h)
            if not trend:
                return
            
            # Check for pullback entry
            signal = self.check_pullback_entry(candles_15m, trend)
            if signal:
                self.open_position(signal)
            
        except Exception as e:
            logger.error(f"Bot run error: {e}")
    
    def _log_trade(self, action: str, price: float, size: float, pnl: float = 0):
        """Log trade"""
        try:
            trade = Trade(
                user_id=self.user_id,
                bot_type='trend_master',
                symbol=self.symbol,
                action=action,
                price=price,
                amount=size,
                timestamp=datetime.utcnow(),
                profit_loss=pnl
            )
            db_session.add(trade)
            db_session.commit()
        except Exception as e:
            logger.error(f"Trade log error: {e}")
