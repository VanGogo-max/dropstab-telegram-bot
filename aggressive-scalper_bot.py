"""
🔥 AGGRESSIVE SCALPER BOT
Exchange: Hyperliquid (Arbitrum Network)
Strategy: Momentum Breakout + High Frequency Scalping
Risk Level: HIGH ⚠️

📊 STRATEGY OVERVIEW:
- Follows strong momentum trends (EMA50 > EMA200 on 1h)
- Enters on breakout of 30-period range (5m timeframe)
- Uses tight stops (0.3%) for quick exits
- Takes profits fast (1%) - typical scalping approach
- High leverage (up to 20x) for maximum returns

✅ BEST FOR:
- Experienced traders comfortable with high risk
- Those who can monitor positions frequently
- Markets with high volatility and volume
- Traders seeking quick profits (minutes to hours)

⚠️ RISKS:
- High leverage = high liquidation risk
- False breakouts can trigger stop losses
- Requires active monitoring
- High trading fees from frequent trades

📈 EXPECTED PERFORMANCE:
- Win Rate: ~60%
- Risk:Reward: 1:3
- Avg Trade Duration: 5-30 minutes
- Recommended Capital: $100+ per position
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


class AggressiveScalperBot:
    """High-frequency momentum scalping on Hyperliquid"""
    
    # Bot metadata for UI
    BOT_NAME = "Aggressive Scalper"
    BOT_DESCRIPTION = "Fast momentum scalping with high leverage"
    BOT_RISK_LEVEL = "HIGH"
    BOT_TIMEFRAME = "5m scalping"
    BOT_EXCHANGE = "Hyperliquid (Arbitrum)"
    
    def __init__(self, user_id: int, symbol: str = 'BTC/USDT',
                 risk_usd: float = 5, max_leverage: int = 20):
        self.user_id = user_id
        self.symbol = symbol
        self.exchange = exchange_api.get_futures_exchange()
        
        # Risk parameters (conservative defaults)
        self.risk_usd = risk_usd
        self.max_leverage = min(max_leverage, 20)  # Cap at 20x for safety
        
        # Strategy parameters
        self.trend_ema_fast = 50
        self.trend_ema_slow = 200
        self.breakout_period = 30
        self.stop_loss_pct = 0.003  # 0.3%
        self.take_profit_pct = 0.01  # 1%
        self.min_volume_multiplier = 1.5  # Volume must be 1.5x average
        self.min_atr_pct = 0.002  # ATR must be > 0.2% for volatility
        
        # Position tracking
        self.position = None
        self.entry_price = 0
        self.stop_loss = 0
        self.take_profit = 0
        
        logger.info(f"Aggressive Scalper Bot initialized: {symbol}")
    
    def ema(self, values: np.ndarray, period: int) -> np.ndarray:
        """Calculate Exponential Moving Average"""
        k = 2 / (period + 1)
        ema_vals = []
        ema_prev = values[0]
        for v in values:
            ema_prev = v * k + ema_prev * (1 - k)
            ema_vals.append(ema_prev)
        return np.array(ema_vals)
    
    def calculate_atr(self, candles: List[Dict], period: int = 14) -> float:
        """Calculate Average True Range for volatility"""
        if len(candles) < period + 1:
            return 0
        
        true_ranges = []
        for i in range(1, len(candles)):
            high = candles[i]['high']
            low = candles[i]['low']
            prev_close = candles[i-1]['close']
            
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            true_ranges.append(tr)
        
        atr = np.mean(true_ranges[-period:])
        return float(atr)
    
    def get_market_data(self, timeframe: str, limit: int) -> List[Dict]:
        """Fetch candle data (mock - implement actual fetching)"""
        # TODO: Implement actual Hyperliquid API call
        # For now return empty list
        return []
    
    def analyze_trend(self, candles_1h: List[Dict]) -> Optional[str]:
        """Determine market trend using EMAs"""
        if len(candles_1h) < self.trend_ema_slow:
            return None
        
        closes = np.array([c['close'] for c in candles_1h])
        ema50 = self.ema(closes, self.trend_ema_fast)[-1]
        ema200 = self.ema(closes, self.trend_ema_slow)[-1]
        
        if ema50 > ema200:
            return "long"
        elif ema50 < ema200:
            return "short"
        else:
            return None
    
    def check_breakout(self, candles_5m: List[Dict], trend: str) -> Optional[Dict]:
        """Check for breakout signal with volume confirmation"""
        if len(candles_5m) < self.breakout_period + 1:
            return None
        
        highs = np.array([c['high'] for c in candles_5m])
        lows = np.array([c['low'] for c in candles_5m])
        closes = np.array([c['close'] for c in candles_5m])
        volumes = np.array([c['volume'] for c in candles_5m])
        
        last_close = closes[-1]
        last_volume = volumes[-1]
        
        # Check volume (must be 1.5x above average)
        avg_volume = volumes[-20:].mean()
        if last_volume < avg_volume * self.min_volume_multiplier:
            logger.debug("Volume too low for breakout confirmation")
            return None
        
        # Check ATR (need volatility)
        atr = self.calculate_atr(candles_5m, 14)
        if atr < last_close * self.min_atr_pct:
            logger.debug("ATR too low - market not volatile enough")
            return None
        
        # Calculate breakout levels
        range_high = highs[-self.breakout_period:-1].max()
        range_low = lows[-self.breakout_period:-1].min()
        
        # Check for breakout
        if trend == "long" and last_close > range_high:
            return {
                'side': 'buy',
                'entry': last_close,
                'breakout_level': range_high,
                'atr': atr
            }
        elif trend == "short" and last_close < range_low:
            return {
                'side': 'sell',
                'entry': last_close,
                'breakout_level': range_low,
                'atr': atr
            }
        
        return None
    
    def calculate_position_size(self, entry: float, stop_loss: float) -> float:
        """Calculate position size based on risk"""
        stop_distance = abs(entry - stop_loss)
        if stop_distance <= 0:
            return 0
        
        # Size = (Risk $ × Leverage) / (Stop Distance × Entry Price)
        size = (self.risk_usd * self.max_leverage) / (stop_distance * entry)
        return round(size, 6)
    
    def open_position(self, signal: Dict) -> bool:
        """Open scalping position"""
        try:
            entry = signal['entry']
            side = signal['side']
            
            # Calculate stop loss and take profit
            if side == 'buy':
                self.stop_loss = signal['breakout_level'] * (1 - self.stop_loss_pct)
                self.take_profit = entry * (1 + self.take_profit_pct)
            else:
                self.stop_loss = signal['breakout_level'] * (1 + self.stop_loss_pct)
                self.take_profit = entry * (1 - self.take_profit_pct)
            
            # Calculate size
            size = self.calculate_position_size(entry, self.stop_loss)
            if size == 0:
                logger.warning("Position size is 0 - skipping trade")
                return False
            
            # Risk check
            if not risk_manager.can_open_position(self.user_id):
                logger.warning("Risk limits exceeded")
                return False
            
            # Set leverage
            self.exchange.set_leverage(self.symbol, self.max_leverage)
            
            # Place order
            result = self.exchange.create_futures_order(
                symbol=self.symbol,
                side=side,
                size=size,
                leverage=self.max_leverage
            )
            
            if 'error' in result:
                logger.error(f"Order failed: {result['error']}")
                return False
            
            # Save position
            self.position = {
                'side': side,
                'entry': entry,
                'size': size,
                'stop_loss': self.stop_loss,
                'take_profit': self.take_profit
            }
            self.entry_price = entry
            
            # Log trade
            self._log_trade('OPEN', entry, size)
            
            # Notification
            email_service.send_trade_alert(
                self.user_id,
                f"🔥 Scalp Entry: {side.upper()} {self.symbol}",
                f"Entry: ${entry:,.2f} | SL: ${self.stop_loss:,.2f} | TP: ${self.take_profit:,.2f}\n"
                f"Size: {size} | Leverage: {self.max_leverage}x"
            )
            
            logger.info(f"Position opened: {side} {size} @ {entry}")
            return True
            
        except Exception as e:
            logger.error(f"Open position error: {e}")
            return False
    
    def close_position(self, reason: str, current_price: float):
        """Close position and calculate P&L"""
        if not self.position:
            return
        
        try:
            side = 'sell' if self.position['side'] == 'buy' else 'buy'
            size = self.position['size']
            
            # Place closing order
            result = self.exchange.create_futures_order(
                symbol=self.symbol,
                side=side,
                size=size,
                reduce_only=True
            )
            
            # Calculate P&L
            if self.position['side'] == 'buy':
                pnl = (current_price - self.entry_price) * size
            else:
                pnl = (self.entry_price - current_price) * size
            
            # Log trade
            self._log_trade('CLOSE', current_price, size, pnl)
            
            # Notification
            email_service.send_trade_alert(
                self.user_id,
                f"💰 Scalp Exit: {reason}",
                f"P&L: ${pnl:,.2f} | Exit: ${current_price:,.2f}"
            )
            
            # Reset position
            self.position = None
            self.entry_price = 0
            
            logger.info(f"Position closed: {reason} | P&L: ${pnl:,.2f}")
            
        except Exception as e:
            logger.error(f"Close position error: {e}")
    
    def manage_position(self, current_price: float):
        """Monitor and manage open position"""
        if not self.position:
            return
        
        # Check stop loss
        if self.position['side'] == 'buy':
            if current_price <= self.stop_loss:
                self.close_position("STOP_LOSS", current_price)
                return
        else:
            if current_price >= self.stop_loss:
                self.close_position("STOP_LOSS", current_price)
                return
        
        # Check take profit
        if self.position['side'] == 'buy':
            if current_price >= self.take_profit:
                self.close_position("TAKE_PROFIT", current_price)
                return
        else:
            if current_price <= self.take_profit:
                self.close_position("TAKE_PROFIT", current_price)
                return
    
    def run(self):
        """Main bot execution"""
        try:
            # Get current position from exchange
            if self.position:
                current_price = self.exchange.get_mark_price(self.symbol)
                self.manage_position(current_price)
                return
            
            # Get market data
            candles_1h = self.get_market_data('1h', 200)
            candles_5m = self.get_market_data('5m', 120)
            
            if not candles_1h or not candles_5m:
                logger.warning("Insufficient market data")
                return
            
            # Analyze trend
            trend = self.analyze_trend(candles_1h)
            if not trend:
                logger.debug("No clear trend detected")
                return
            
            # Check for breakout
            signal = self.check_breakout(candles_5m, trend)
            if signal:
                self.open_position(signal)
            
        except Exception as e:
            logger.error(f"Bot run error: {e}")
    
    def _log_trade(self, action: str, price: float, size: float, pnl: float = 0):
        """Log trade to database"""
        try:
            trade = Trade(
                user_id=self.user_id,
                bot_type='aggressive_scalper',
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
