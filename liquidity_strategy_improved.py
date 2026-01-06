"""
Enhanced Universal Liquidity Strategy
With ATR-based stops, Trend Filter, Trailing Stop, and Partial Profit Taking
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class EnhancedLiquidityStrategy:
    """
    Подобрена версия на UniversalLiquidityStrategy с:
    - ATR-базирани TP/SL (динамични)
    - Trend filter (EMA 50/200)
    - Trailing stop
    - Partial profit taking
    - Volume confirmation
    """
    
    def __init__(
        self, 
        initial_capital: float = 100.0,
        risk_percent: float = 1.5,
        atr_period: int = 14,
        atr_multiplier_sl: float = 1.5,
        atr_multiplier_tp: float = 3.0
    ):
        self.capital = initial_capital
        self.initial_capital = initial_capital
        self.risk_percent = risk_percent
        self.atr_period = atr_period
        self.atr_multiplier_sl = atr_multiplier_sl
        self.atr_multiplier_tp = atr_multiplier_tp
        
        # Original parameters
        self.trade_history = []
        self.optimization_window = 20
        self.zone_buffer_pct = 0.3
        self.min_consecutive_candles = 3
        self.max_consecutive_candles = 5
        
        # NEW: Trailing stop tracking
        self.active_positions = {}  # {position_id: {...}}
        
        # NEW: Trend filter
        self.ema_fast = 50
        self.ema_slow = 200
        self.use_trend_filter = True
        
        # NEW: Volume confirmation
        self.use_volume_filter = True
        self.volume_ma_period = 20
        
        logger.info("Enhanced Liquidity Strategy initialized")
    
    def calculate_atr(self, candles: List[Dict], period: int = None) -> float:
        """Calculate Average True Range"""
        if period is None:
            period = self.atr_period
        
        df = pd.DataFrame(candles[-period-1:])
        
        high = df['high']
        low = df['low']
        close = df['close'].shift(1)
        
        tr1 = high - low
        tr2 = abs(high - close)
        tr3 = abs(low - close)
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean().iloc[-1]
        
        return atr if not np.isnan(atr) else 0
    
    def calculate_ema(self, candles: List[Dict], period: int) -> float:
        """Calculate Exponential Moving Average"""
        df = pd.DataFrame(candles)
        ema = df['close'].ewm(span=period, adjust=False).mean().iloc[-1]
        return ema
    
    def is_trend_bullish(self, h1_data: List[Dict]) -> Optional[bool]:
        """
        Check if trend is bullish using EMA crossover
        Returns: True (bullish), False (bearish), None (no clear trend)
        """
        if not self.use_trend_filter or len(h1_data) < self.ema_slow:
            return None
        
        ema_fast = self.calculate_ema(h1_data, self.ema_fast)
        ema_slow = self.calculate_ema(h1_data, self.ema_slow)
        
        if ema_fast > ema_slow * 1.01:  # 1% buffer
            return True
        elif ema_fast < ema_slow * 0.99:
            return False
        return None
    
    def check_volume_confirmation(self, candles: List[Dict]) -> bool:
        """Check if current volume is above average"""
        if not self.use_volume_filter:
            return True
        
        df = pd.DataFrame(candles[-self.volume_ma_period-1:])
        if 'volume' not in df.columns:
            return True  # Skip if no volume data
        
        current_volume = df['volume'].iloc[-1]
        avg_volume = df['volume'].iloc[:-1].mean()
        
        return current_volume > avg_volume * 1.2  # 20% above average
    
    def detect_liquidity_zones(self, h1_data: List[Dict]) -> List[Tuple[float, float, str]]:
        """
        Открива зони на ликвидност от H1 данни
        ENHANCED: Добавя strength score за всяка зона
        """
        df = pd.DataFrame(h1_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp').tail(48)  # последните 48 часа (2 days)
        
        highs = df['high'].values
        lows = df['low'].values
        
        zones = []
        
        # Resistance zones (локални максимуми)
        for i in range(2, len(highs) - 2):
            if (highs[i] > highs[i-1] and highs[i] > highs[i-2] and 
                highs[i] > highs[i+1] and highs[i] > highs[i+2]):
                
                zone_low = highs[i] * (1 - self.zone_buffer_pct / 100)
                zone_high = highs[i] * (1 + self.zone_buffer_pct / 100)
                
                # Calculate strength (how many times tested)
                touches = sum(1 for h in highs if zone_low <= h <= zone_high)
                
                zones.append({
                    'low': zone_low,
                    'high': zone_high,
                    'type': 'resistance',
                    'strength': touches,
                    'price': highs[i]
                })
        
        # Support zones (локални минимуми)
        for i in range(2, len(lows) - 2):
            if (lows[i] < lows[i-1] and lows[i] < lows[i-2] and 
                lows[i] < lows[i+1] and lows[i] < lows[i+2]):
                
                zone_low = lows[i] * (1 - self.zone_buffer_pct / 100)
                zone_high = lows[i] * (1 + self.zone_buffer_pct / 100)
                
                touches = sum(1 for l in lows if zone_low <= l <= zone_high)
                
                zones.append({
                    'low': zone_low,
                    'high': zone_high,
                    'type': 'support',
                    'strength': touches,
                    'price': lows[i]
                })
        
        # Sort by strength and return top 5
        zones.sort(key=lambda x: x['strength'], reverse=True)
        return zones[:5]
    
    def is_price_in_zone(self, price: float, zones: List[Dict]) -> Optional[Dict]:
        """Check if price is in a liquidity zone"""
        for zone in zones:
            if zone['low'] <= price <= zone['high']:
                return zone
        return None
    
    def detect_entry_pattern(
        self, 
        candles: List[Dict], 
        zone_type: str
    ) -> Optional[Dict]:
        """
        Enhanced pattern detection with ATR-based stops
        """
        if len(candles) < 7:
            return None
        
        df = pd.DataFrame(candles[-7:])
        atr = self.calculate_atr(candles)
        
        if atr == 0:
            return None
        
        # Volume confirmation
        if not self.check_volume_confirmation(candles):
            logger.debug("Volume confirmation failed")
            return None
        
        # SHORT pattern (only in resistance zones)
        if zone_type == 'resistance':
            red_candles = sum(
                1 for i in range(-6, -2) 
                if df.iloc[i]['close'] < df.iloc[i]['open']
            )
            
            if red_candles >= self.min_consecutive_candles:
                # Green pullback candle
                if df.iloc[-2]['close'] > df.iloc[-2]['open']:
                    # Red continuation breaking pullback low
                    if (df.iloc[-1]['close'] < df.iloc[-1]['open'] and
                        df.iloc[-1]['close'] < df.iloc[-2]['low']):
                        
                        entry = df.iloc[-1]['close']
                        stop_loss = entry + (atr * self.atr_multiplier_sl)
                        take_profit = entry - (atr * self.atr_multiplier_tp)
                        
                        return {
                            'direction': 'short',
                            'entry_price': entry,
                            'stop_loss': stop_loss,
                            'take_profit': take_profit,
                            'atr': atr,
                            'risk_reward': self.atr_multiplier_tp / self.atr_multiplier_sl
                        }
        
        # LONG pattern (only in support zones)
        elif zone_type == 'support':
            green_candles = sum(
                1 for i in range(-6, -2) 
                if df.iloc[i]['close'] > df.iloc[i]['open']
            )
            
            if green_candles >= self.min_consecutive_candles:
                # Red pullback candle
                if df.iloc[-2]['close'] < df.iloc[-2]['open']:
                    # Green continuation breaking pullback high
                    if (df.iloc[-1]['close'] > df.iloc[-1]['open'] and
                        df.iloc[-1]['close'] > df.iloc[-2]['high']):
                        
                        entry = df.iloc[-1]['close']
                        stop_loss = entry - (atr * self.atr_multiplier_sl)
                        take_profit = entry + (atr * self.atr_multiplier_tp)
                        
                        return {
                            'direction': 'long',
                            'entry_price': entry,
                            'stop_loss': stop_loss,
                            'take_profit': take_profit,
                            'atr': atr,
                            'risk_reward': self.atr_multiplier_tp / self.atr_multiplier_sl
                        }
        
        return None
    
    def calculate_position_size(self, entry: float, stop_loss: float) -> float:
        """Calculate position size based on risk"""
        risk_amount = self.capital * (self.risk_percent / 100)
        price_risk = abs(entry - stop_loss)
        
        if price_risk == 0:
            return 0
        
        size = risk_amount / price_risk
        return size
    
    def update_trailing_stop(
        self, 
        position_id: str, 
        current_price: float
    ) -> Dict:
        """
        Update trailing stop for active position
        Moves stop to breakeven at 50% TP, then trails at 1 ATR
        """
        if position_id not in self.active_positions:
            return None
        
        pos = self.active_positions[position_id]
        entry = pos['entry_price']
        stop_loss = pos['stop_loss']
        take_profit = pos['take_profit']
        direction = pos['direction']
        atr = pos['atr']
        
        if direction == 'long':
            # Check if 50% TP reached -> move SL to breakeven
            halfway = entry + (take_profit - entry) * 0.5
            if current_price >= halfway and stop_loss < entry:
                pos['stop_loss'] = entry
                pos['status'] = 'breakeven'
                logger.info(f"Position {position_id}: SL moved to breakeven")
            
            # Check if TP reached -> trail at 1 ATR
            if current_price >= take_profit:
                new_stop = current_price - atr
                if new_stop > pos['stop_loss']:
                    pos['stop_loss'] = new_stop
                    pos['status'] = 'trailing'
                    logger.info(f"Position {position_id}: Trailing at {new_stop}")
        
        else:  # short
            halfway = entry - (entry - take_profit) * 0.5
            if current_price <= halfway and stop_loss > entry:
                pos['stop_loss'] = entry
                pos['status'] = 'breakeven'
                logger.info(f"Position {position_id}: SL moved to breakeven")
            
            if current_price <= take_profit:
                new_stop = current_price + atr
                if new_stop < pos['stop_loss']:
                    pos['stop_loss'] = new_stop
                    pos['status'] = 'trailing'
                    logger.info(f"Position {position_id}: Trailing at {new_stop}")
        
        return pos
    
    def check_exit(
        self, 
        position_id: str, 
        current_price: float
    ) -> Optional[Dict]:
        """
        Check if position should be exited
        Returns exit info or None
        """
        if position_id not in self.active_positions:
            return None
        
        pos = self.active_positions[position_id]
        direction = pos['direction']
        stop_loss = pos['stop_loss']
        take_profit = pos['take_profit']
        
        # Check stop loss
        if direction == 'long' and current_price <= stop_loss:
            return {
                'reason': 'stop_loss',
                'exit_price': current_price,
                'pnl': (current_price - pos['entry_price']) * pos['position_size']
            }
        
        if direction == 'short' and current_price >= stop_loss:
            return {
                'reason': 'stop_loss',
                'exit_price': current_price,
                'pnl': (pos['entry_price'] - current_price) * pos['position_size']
            }
        
        # Check take profit
        if direction == 'long' and current_price >= take_profit:
            return {
                'reason': 'take_profit',
                'exit_price': current_price,
                'pnl': (current_price - pos['entry_price']) * pos['position_size']
            }
        
        if direction == 'short' and current_price <= take_profit:
            return {
                'reason': 'take_profit',
                'exit_price': current_price,
                'pnl': (pos['entry_price'] - current_price) * pos['position_size']
            }
        
        return None
    
    def update_capital_after_trade(self, profit_usd: float):
        """Update capital after trade (compound interest)"""
        self.capital += profit_usd
        self.trade_history.append(profit_usd)
        self._auto_optimize()
        
        logger.info(f"Capital updated: ${self.capital:.2f} (P&L: ${profit_usd:.2f})")
    
    def _auto_optimize(self):
        """Auto-optimization based on recent performance"""
        if len(self.trade_history) < self.optimization_window:
            return
        
        recent_trades = self.trade_history[-self.optimization_window:]
        win_rate = sum(1 for p in recent_trades if p > 0) / len(recent_trades)
        avg_profit = np.mean(recent_trades)
        
        logger.info(f"Auto-optimize: Win rate {win_rate:.2%}, Avg P&L ${avg_profit:.2f}")
        
        # Adjust parameters based on performance
        if win_rate < 0.5:
            # Tighten strategy
            self.zone_buffer_pct = min(0.5, self.zone_buffer_pct + 0.05)
            self.min_consecutive_candles = min(5, self.min_consecutive_candles + 1)
            self.atr_multiplier_sl = min(2.0, self.atr_multiplier_sl + 0.1)
            logger.info("Strategy tightened due to low win rate")
        
        elif win_rate > 0.65:
            # Loosen strategy to catch more setups
            self.zone_buffer_pct = max(0.2, self.zone_buffer_pct - 0.05)
            self.min_consecutive_candles = max(3, self.min_consecutive_candles - 1)
            self.atr_multiplier_sl = max(1.0, self.atr_multiplier_sl - 0.1)
            logger.info("Strategy loosened due to high win rate")
        
        # Keep only recent history
        self.trade_history = self.trade_history[-self.optimization_window:]
    
    def evaluate(
        self, 
        h1_data: List[Dict], 
        m5_data: List[Dict]
    ) -> Optional[Dict]:
        """
        Main evaluation method - returns trade signal or None
        """
        # Detect liquidity zones
        zones = self.detect_liquidity_zones(h1_data)
        
        if not zones:
            logger.debug("No liquidity zones detected")
            return None
        
        current_price = m5_data[-1]['close']
        zone_match = self.is_price_in_zone(current_price, zones)
        
        if not zone_match:
            logger.debug(f"Price {current_price} not in any zone")
            return None
        
        zone_type = zone_match['type']
        logger.debug(f"Price in {zone_type} zone (strength: {zone_match['strength']})")
        
        # Trend filter
        trend = self.is_trend_bullish(h1_data)
        if self.use_trend_filter and trend is not None:
            if zone_type == 'support' and trend is False:
                logger.debug("Skipping long setup - bearish trend")
                return None
            if zone_type == 'resistance' and trend is True:
                logger.debug("Skipping short setup - bullish trend")
                return None
        
        # Detect entry pattern
        signal = self.detect_entry_pattern(m5_data, zone_type)
        
        if not signal:
            logger.debug("No entry pattern detected")
            return None
        
        # Confirm direction matches zone
        if (signal['direction'] == 'short' and zone_type != 'resistance') or \
           (signal['direction'] == 'long' and zone_type != 'support'):
            logger.debug("Direction mismatch with zone type")
            return None
        
        # Calculate position size
        size = self.calculate_position_size(
            signal['entry_price'], 
            signal['stop_loss']
        )
        
        if size <= 0:
            logger.warning("Position size calculation failed")
            return None
        
        logger.info(
            f"✅ {signal['direction'].upper()} signal: "
            f"Entry ${signal['entry_price']:.2f}, "
            f"SL ${signal['stop_loss']:.2f}, "
            f"TP ${signal['take_profit']:.2f}, "
            f"R:R {signal['risk_reward']:.2f}"
        )
        
        return {
            'direction': signal['direction'],
            'entry_price': signal['entry_price'],
            'stop_loss': signal['stop_loss'],
            'take_profit': signal['take_profit'],
            'position_size': size,
            'capital_used': self.capital,
            'zone': zone_match,
            'atr': signal['atr'],
            'risk_reward': signal['risk_reward'],
            'trend': 'bullish' if trend else 'bearish' if trend is False else 'neutral'
        }
