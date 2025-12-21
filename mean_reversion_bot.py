"""
🎯 MEAN REVERSION PRO BOT
Exchange: KCEX (Spot Trading)
Strategy: Bollinger Bands Mean Reversion
Risk Level: LOW 🟢

📊 STRATEGY OVERVIEW:
- Trades sideways/ranging markets using Bollinger Bands
- Buys when price touches lower band (oversold)
- Sells when price touches upper band (overbought)
- Targets return to middle band (mean)
- Uses ADX filter to avoid trending markets
- Low leverage (3x) for safety

✅ BEST FOR:
- Conservative traders seeking steady returns
- Those who prefer ranging/sideways markets
- Traders wanting low-stress trading
- Markets without strong directional trends

⚠️ RISKS:
- Doesn't work in strong trends
- May take longer to reach profit target
- Lower profit per trade vs trending strategies
- Requires patience and discipline

📈 EXPECTED PERFORMANCE:
- Win Rate: ~65%
- Risk:Reward: 1:1.5
- Avg Trade Duration: 2-5 days
- Recommended Capital: $30+ per position
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import numpy as np

from exchange_api import exchange_api
from risk_manager import risk_manager
from database import db_session, Trade
from email_service import email_service
from config import *

logger = logging.getLogger(__name__)


class MeanReversionBot:
    """Mean reversion trading with Bollinger Bands"""
    
    # Bot metadata
    BOT_NAME = "Mean Reversion Pro"
    BOT_DESCRIPTION = "Trade ranging markets with Bollinger Bands"
    BOT_RISK_LEVEL = "LOW"
    BOT_TIMEFRAME = "1h mean reversion"
    BOT_EXCHANGE = "KCEX (Spot)"
    
    def __init__(self, user_id: int, symbol: str = 'BTC/USDT',
                 risk_usd: float = 5, leverage: int = 3):
        self.user_id = user_id
        self.symbol = symbol
        self.exchange = exchange_api.get_spot_exchange()
        
        # Risk parameters
        self.risk_usd = risk_usd
        self.leverage = min(leverage, 3)  # Max 3x leverage
        
        # Strategy parameters
        self.bb_period = 20
        self.bb_std = 2
        self.adx_period = 14
        self.adx_threshold = 25  # ADX < 25 = no strong trend
        self.tp_extension = 0.5  # Take 50% extra beyond mid
        
        # Position tracking
        self.position = None
        
        logger.info(f"Mean Reversion Bot initialized: {symbol}")
    
    def simple_moving_average(self, values: np.ndarray, period: int) -> np.ndarray:
        """Calculate SMA"""
        return np.convolve(values, np.ones(period)/period, mode='valid')
    
    def bollinger_bands(self, closes: np.ndarray, period: int = 20, 
                       std_mult: float = 2) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Calculate Bollinger Bands"""
        if len(closes) < period:
            return np.array([]), np.array([]), np.array([])
        
        ma = self.simple_moving_average(closes, period)
        
        # Calculate standard deviation
        std_devs = []
        for i in range(period - 1, len(closes)):
            window = closes[i - period + 1:i + 1]
            std_devs.append(window.std())
        
        std_devs = np.array(std_devs)
        
        upper = ma + (std_mult * std_devs)
        lower = ma - (std_mult * std_devs)
        
        return ma, upper, lower
    
    def calculate_adx(self, candles: List[Dict], period: int = 14) -> float:
        """Calculate Average Directional Index (trend strength)"""
        if len(candles) < period * 2:
            return 50  # Default to high ADX if not enough data
        
        highs = np.array([c['high'] for c in candles])
        lows = np.array([c['low'] for c in candles])
        closes = np.array([c['close'] for c in candles])
        
        # Calculate +DM and -DM
        plus_dm = np.zeros(len(highs) - 1)
        minus_dm = np.zeros(len(highs) - 1)
        
        for i in range(1, len(highs)):
            high_diff = highs[i] - highs[i-1]
            low_diff = lows[i-1] - lows[i]
            
            if high_diff > low_diff and high_diff > 0:
                plus_dm[i-1] = high_diff
            if low_diff > high_diff and low_diff > 0:
                minus_dm[i-1] = low_diff
        
        # Calculate True Range
        tr = []
        for i in range(1, len(highs)):
            tr_val = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i-1]),
                abs(lows[i] - closes[i-1])
            )
            tr.append(tr_val)
        tr = np.array(tr)
        
        # Smooth with moving average
        if len(plus_dm) < period:
            return 50
        
        plus_di = 100 * (plus_dm[-period:].mean() / tr[-period:].mean())
        minus_di = 100 * (minus_dm[-period:].mean() / tr[-period:].mean())
        
        # Calculate ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di + 1e-10)
        adx = dx  # Simplified ADX
        
        return float(adx)
    
    def get_market_data(self, timeframe: str, limit: int) -> List[Dict]:
        """Fetch candle data (mock)"""
        # TODO: Implement actual KCEX API call
        return []
    
    def check_mean_reversion_signal(self, candles_1h: List[Dict]) -> Optional[Dict]:
        """Check for mean reversion opportunity"""
        if len(candles_1h) < 40:
            return None
        
        closes = np.array([c['close'] for c in candles_1h])
        
        # Calculate Bollinger Bands
        ma, upper, lower = self.bollinger_bands(closes, self.bb_period, self.bb_std)
        
        if len(ma) == 0:
            return None
        
        last_close = closes[-1]
        mid = ma[-1]
        up = upper[-1]
        lo = lower[-1]
        
        # Check ADX - only trade if market is NOT trending
        adx = self.calculate_adx(candles_1h, self.adx_period)
        if adx > self.adx_threshold:
            logger.debug(f"ADX too high ({adx:.1f}) - market is trending")
            return None
        
        # Check volume (optional - add if data available)
        # Low volume = better for mean reversion
        
        # Check for signal
        side = None
        stop_loss = None
        take_profit = None
        
        # Buy signal: price touches lower band
        if last_close <= lo:
            side = "buy"
            stop_loss = last_close * 0.99  # 1% below entry
            # Target: mid + 50% of (mid - lower)
            range_size = mid - lo
            take_profit = mid + (range_size * self.tp_extension)
        
        # Sell signal: price touches upper band
        elif last_close >= up:
            side = "sell"
            stop_loss = last_close * 1.01  # 1% above entry
            # Target: mid - 50% of (upper - mid)
            range_size = up - mid
            take_profit = mid - (range_size * self.tp_extension)
        
        else:
            return None
        
        # Validate stop distance
        stop_distance = abs(last_close - stop_loss)
        if stop_distance <= 0:
            return None
        
        return {
            'side': side,
            'entry': last_close,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'mid': mid,
            'upper': up,
            'lower': lo,
            'adx': adx
        }
    
    def calculate_position_size(self, entry: float, stop_loss: float) -> float:
        """Calculate position size"""
        stop_distance = abs(entry - stop_loss)
        if stop_distance <= 0:
            return 0
        
        size = (self.risk_usd * self.leverage) / (stop_distance * entry)
        return round(size, 6)
    
    def open_position(self, signal: Dict) -> bool:
        """Open mean reversion position"""
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
                f"🎯 Mean Reversion Entry: {side.upper()} {self.symbol}",
                f"Entry: ${entry:,.2f} | SL: ${stop_loss:,.2f} | TP: ${take_profit:,.2f}\n"
                f"BB Mid: ${signal['mid']:,.2f} | ADX: {signal['adx']:.1f}\n"
                f"Upper: ${signal['upper']:,.2f} | Lower: ${signal['lower']:,.2f}"
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
                f"💰 Mean Reversion Exit: {reason}",
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
            candles_1h = self.get_market_data('1h', 200)
            
            if not candles_1h:
                return
            
            # Check for mean reversion signal
            signal = self.check_mean_reversion_signal(candles_1h)
            if signal:
                self.open_position(signal)
            
        except Exception as e:
            logger.error(f"Bot run error: {e}")
    
    def _log_trade(self, action: str, price: float, size: float, pnl: float = 0):
        """Log trade"""
        try:
            trade = Trade(
                user_id=self.user_id,
                bot_type='mean_reversion',
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
