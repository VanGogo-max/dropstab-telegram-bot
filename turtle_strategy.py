"""
Turtle Trading Strategy - Classic Trend Following System
Based on the legendary strategy from Richard Dennis and William Eckhardt
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class TurtleStrategy:
    """
    Turtle Trading System Implementation
    
    Rules:
    - System 1: 20-day breakout (faster but more whipsaws)
    - System 2: 55-day breakout (slower but more reliable)
    - Exit: 10-day reverse breakout
    - Position sizing: Based on ATR (N)
    - Pyramiding: Add up to 4 units (0.5N apart)
    """
    
    def __init__(
        self,
        initial_capital: float = 10000.0,
        system: int = 2,  # 1 or 2
        breakout_period: int = 55,
        exit_period: int = 10,
        atr_period: int = 20,
        max_units: int = 4,
        unit_risk: float = 0.01,  # 1% risk per unit
        max_portfolio_risk: float = 0.02  # 2% total portfolio risk
    ):
        self.capital = initial_capital
        self.initial_capital = initial_capital
        self.system = system
        self.breakout_period = breakout_period if system == 2 else 20
        self.exit_period = exit_period
        self.atr_period = atr_period
        self.max_units = max_units
        self.unit_risk = unit_risk
        self.max_portfolio_risk = max_portfolio_risk
        
        # Position tracking
        self.positions = {}  # {symbol: {...}}
        self.trade_history = []
        
        # Performance metrics
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        
        logger.info(
            f"Turtle Strategy initialized: System {system}, "
            f"Breakout {self.breakout_period}, Exit {exit_period}"
        )
    
    def calculate_atr(self, candles: List[Dict], period: int = None) -> float:
        """
        Calculate Average True Range (N in Turtle terminology)
        """
        if period is None:
            period = self.atr_period
        
        if len(candles) < period + 1:
            return 0
        
        df = pd.DataFrame(candles[-(period+1):])
        
        high = df['high']
        low = df['low']
        close = df['close'].shift(1)
        
        tr1 = high - low
        tr2 = abs(high - close)
        tr3 = abs(low - close)
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean().iloc[-1]
        
        return atr if not np.isnan(atr) else 0
    
    def calculate_breakout_levels(
        self, 
        candles: List[Dict]
    ) -> Dict[str, float]:
        """
        Calculate breakout levels for entry and exit
        """
        df = pd.DataFrame(candles)
        
        # Entry breakout levels
        entry_high = df['high'].tail(self.breakout_period).max()
        entry_low = df['low'].tail(self.breakout_period).min()
        
        # Exit breakout levels
        exit_high = df['high'].tail(self.exit_period).max()
        exit_low = df['low'].tail(self.exit_period).min()
        
        return {
            'entry_long': entry_high,
            'entry_short': entry_low,
            'exit_long': exit_low,
            'exit_short': exit_high
        }
    
    def calculate_position_size(
        self, 
        symbol: str,
        atr: float,
        price: float
    ) -> float:
        """
        Calculate position size based on ATR (Turtle's Dollar Volatility)
        Dollar Volatility = N * Dollars per Point
        Unit Size = (1% of Capital) / Dollar Volatility
        """
        if atr == 0:
            return 0
        
        # Calculate unit size
        risk_amount = self.capital * self.unit_risk
        dollar_volatility = atr * price  # Simplified for crypto
        unit_size = risk_amount / dollar_volatility
        
        # Check if we already have positions
        existing_units = 0
        if symbol in self.positions:
            existing_units = self.positions[symbol]['units']
        
        # Don't exceed max units
        if existing_units >= self.max_units:
            return 0
        
        # Check total portfolio risk
        total_risk = (existing_units + 1) * self.unit_risk
        if total_risk > self.max_portfolio_risk:
            logger.warning(f"Max portfolio risk reached for {symbol}")
            return 0
        
        return unit_size
    
    def check_entry_signal(
        self, 
        symbol: str,
        candles: List[Dict]
    ) -> Optional[Dict]:
        """
        Check for entry signal (breakout)
        """
        if len(candles) < max(self.breakout_period, self.atr_period) + 1:
            return None
        
        current_price = candles[-1]['close']
        prev_price = candles[-2]['close']
        
        levels = self.calculate_breakout_levels(candles[:-1])  # Exclude current
        atr = self.calculate_atr(candles)
        
        if atr == 0:
            return None
        
        # Long entry: Price breaks above N-day high
        if (prev_price <= levels['entry_long'] and 
            current_price > levels['entry_long']):
            
            size = self.calculate_position_size(symbol, atr, current_price)
            
            if size > 0:
                stop_loss = current_price - (2 * atr)  # 2N stop
                
                return {
                    'direction': 'long',
                    'entry_price': current_price,
                    'stop_loss': stop_loss,
                    'position_size': size,
                    'atr': atr,
                    'breakout_level': levels['entry_long'],
                    'reason': f'{self.breakout_period}-day high breakout'
                }
        
        # Short entry: Price breaks below N-day low
        if (prev_price >= levels['entry_short'] and 
            current_price < levels['entry_short']):
            
            size = self.calculate_position_size(symbol, atr, current_price)
            
            if size > 0:
                stop_loss = current_price + (2 * atr)  # 2N stop
                
                return {
                    'direction': 'short',
                    'entry_price': current_price,
                    'stop_loss': stop_loss,
                    'position_size': size,
                    'atr': atr,
                    'breakout_level': levels['entry_short'],
                    'reason': f'{self.breakout_period}-day low breakout'
                }
        
        return None
    
    def check_pyramid_add(
        self, 
        symbol: str,
        candles: List[Dict]
    ) -> Optional[Dict]:
        """
        Check if we should add to existing position (pyramiding)
        Add unit when price moves 0.5N in favorable direction
        """
        if symbol not in self.positions:
            return None
        
        pos = self.positions[symbol]
        
        if pos['units'] >= self.max_units:
            return None
        
        current_price = candles[-1]['close']
        last_entry = pos['last_entry_price']
        atr = self.calculate_atr(candles)
        
        if atr == 0:
            return None
        
        # Long position: Add if price moved up 0.5N
        if pos['direction'] == 'long':
            if current_price >= last_entry + (0.5 * atr):
                size = self.calculate_position_size(symbol, atr, current_price)
                
                if size > 0:
                    return {
                        'action': 'add',
                        'direction': 'long',
                        'entry_price': current_price,
                        'position_size': size,
                        'atr': atr,
                        'reason': 'Pyramiding +0.5N'
                    }
        
        # Short position: Add if price moved down 0.5N
        elif pos['direction'] == 'short':
            if current_price <= last_entry - (0.5 * atr):
                size = self.calculate_position_size(symbol, atr, current_price)
                
                if size > 0:
                    return {
                        'action': 'add',
                        'direction': 'short',
                        'entry_price': current_price,
                        'position_size': size,
                        'atr': atr,
                        'reason': 'Pyramiding -0.5N'
                    }
        
        return None
    
    def check_exit_signal(
        self, 
        symbol: str,
        candles: List[Dict]
    ) -> Optional[Dict]:
        """
        Check for exit signal
        - 10-day reverse breakout
        - 2N stop loss hit
        """
        if symbol not in self.positions:
            return None
        
        pos = self.positions[symbol]
        current_price = candles[-1]['close']
        prev_price = candles[-2]['close']
        
        levels = self.calculate_breakout_levels(candles[:-1])
        
        # Check stop loss (2N rule)
        if pos['direction'] == 'long' and current_price <= pos['stop_loss']:
            pnl = (current_price - pos['avg_entry_price']) * pos['total_size']
            
            return {
                'reason': 'stop_loss',
                'exit_price': current_price,
                'pnl': pnl,
                'pnl_percent': (pnl / (pos['avg_entry_price'] * pos['total_size'])) * 100
            }
        
        if pos['direction'] == 'short' and current_price >= pos['stop_loss']:
            pnl = (pos['avg_entry_price'] - current_price) * pos['total_size']
            
            return {
                'reason': 'stop_loss',
                'exit_price': current_price,
                'pnl': pnl,
                'pnl_percent': (pnl / (pos['avg_entry_price'] * pos['total_size'])) * 100
            }
        
        # Check 10-day exit breakout
        if pos['direction'] == 'long':
            if (prev_price >= levels['exit_long'] and 
                current_price < levels['exit_long']):
                
                pnl = (current_price - pos['avg_entry_price']) * pos['total_size']
                
                return {
                    'reason': f'{self.exit_period}-day low exit',
                    'exit_price': current_price,
                    'pnl': pnl,
                    'pnl_percent': (pnl / (pos['avg_entry_price'] * pos['total_size'])) * 100
                }
        
        if pos['direction'] == 'short':
            if (prev_price <= levels['exit_short'] and 
                current_price > levels['exit_short']):
                
                pnl = (pos['avg_entry_price'] - current_price) * pos['total_size']
                
                return {
                    'reason': f'{self.exit_period}-day high exit',
                    'exit_price': current_price,
                    'pnl': pnl,
                    'pnl_percent': (pnl / (pos['avg_entry_price'] * pos['total_size'])) * 100
                }
        
        return None
    
    def open_position(self, symbol: str, signal: Dict):
        """Open new position"""
        self.positions[symbol] = {
            'direction': signal['direction'],
            'entry_price': signal['entry_price'],
            'avg_entry_price': signal['entry_price'],
            'last_entry_price': signal['entry_price'],
            'stop_loss': signal['stop_loss'],
            'position_size': signal['position_size'],
            'total_size': signal['position_size'],
            'units': 1,
            'atr': signal['atr'],
            'opened_at': datetime.utcnow()
        }
        
        logger.info(
            f"🐢 Turtle {signal['direction'].upper()} opened: {symbol} @ ${signal['entry_price']:.2f}, "
            f"Size: {signal['position_size']:.4f}, SL: ${signal['stop_loss']:.2f}"
        )
    
    def add_to_position(self, symbol: str, signal: Dict):
        """Add unit to existing position (pyramiding)"""
        pos = self.positions[symbol]
        
        # Update average entry price
        total_value = (pos['avg_entry_price'] * pos['total_size']) + \
                     (signal['entry_price'] * signal['position_size'])
        new_total_size = pos['total_size'] + signal['position_size']
        pos['avg_entry_price'] = total_value / new_total_size
        
        # Update position
        pos['total_size'] = new_total_size
        pos['last_entry_price'] = signal['entry_price']
        pos['units'] += 1
        pos['atr'] = signal['atr']
        
        # Adjust stop loss (trail at 2N from new average)
        if pos['direction'] == 'long':
            pos['stop_loss'] = max(pos['stop_loss'], signal['entry_price'] - (2 * signal['atr']))
        else:
            pos['stop_loss'] = min(pos['stop_loss'], signal['entry_price'] + (2 * signal['atr']))
        
        logger.info(
            f"🐢 Turtle ADD unit {pos['units']}/{self.max_units}: {symbol} @ ${signal['entry_price']:.2f}, "
            f"Avg: ${pos['avg_entry_price']:.2f}, New SL: ${pos['stop_loss']:.2f}"
        )
    
    def close_position(self, symbol: str, exit_info: Dict):
        """Close position and update capital"""
        pos = self.positions[symbol]
        
        pnl = exit_info['pnl']
        self.capital += pnl
        
        # Update statistics
        self.total_trades += 1
        if pnl > 0:
            self.winning_trades += 1
        else:
            self.losing_trades += 1
        
        # Save trade history
        self.trade_history.append({
            'symbol': symbol,
            'direction': pos['direction'],
            'entry_price': pos['avg_entry_price'],
            'exit_price': exit_info['exit_price'],
            'size': pos['total_size'],
            'pnl': pnl,
            'pnl_percent': exit_info['pnl_percent'],
            'units': pos['units'],
            'reason': exit_info['reason'],
            'duration': (datetime.utcnow() - pos['opened_at']).total_seconds() / 3600,  # hours
            'capital_after': self.capital
        })
        
        logger.info(
            f"🐢 Turtle CLOSED: {symbol} {pos['direction'].upper()}, "
            f"P&L: ${pnl:.2f} ({exit_info['pnl_percent']:.2f}%), "
            f"Reason: {exit_info['reason']}, Capital: ${self.capital:.2f}"
        )
        
        # Remove position
        del self.positions[symbol]
    
    def evaluate(self, symbol: str, candles: List[Dict]) -> Optional[Dict]:
        """
        Main evaluation method
        Returns: trade action or None
        """
        # Check for exit first
        if symbol in self.positions:
            exit_signal = self.check_exit_signal(symbol, candles)
            if exit_signal:
                self.close_position(symbol, exit_signal)
                return {
                    'action': 'close',
                    **exit_signal
                }
            
            # Check for pyramid add
            add_signal = self.check_pyramid_add(symbol, candles)
            if add_signal:
                self.add_to_position(symbol, add_signal)
                return {
                    'action': 'add',
                    **add_signal
                }
        
        # Check for new entry
        entry_signal = self.check_entry_signal(symbol, candles)
        if entry_signal:
            self.open_position(symbol, entry_signal)
            return {
                'action': 'open',
                **entry_signal
            }
        
        return None
    
    def get_performance_stats(self) -> Dict:
        """Get strategy performance statistics"""
        if self.total_trades == 0:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'roi': 0
            }
        
        win_rate = self.winning_trades / self.total_trades
        total_pnl = self.capital - self.initial_capital
        roi = (total_pnl / self.initial_capital) * 100
        
        recent_pnls = [t['pnl'] for t in self.trade_history[-20:]]
        avg_pnl = np.mean(recent_pnls) if recent_pnls else 0
        
        return {
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'roi': roi,
            'avg_pnl': avg_pnl,
            'capital': self.capital,
            'active_positions': len(self.positions)
        }
