"""
Advanced Grid Trading Bot - Combined Strategy
Combines BaseStrategy architecture with Telegram signal following and advanced grid management

Features from OLD bot:
- Telegram signal parsing ("BTC LONG", "ETH SHORT")
- 5 TP levels with partial close (20% each: 1%, 2%, 3%, 5%, 8%)
- Emergency stop loss (15%)
- Leverage control (capped at 5x)
- Real-time position monitoring

Features from NEW bot:
- BaseStrategy inheritance (integrates with StrategyAutoSelector)
- ATR-based dynamic grid calculation
- Volatility analysis
- Auto rebalancing
- Performance tracking
- Clean modular architecture

Author: Combined by Claude
Date: 2025-01-18
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

from base_strategy import BaseStrategy


class AdvancedGridBot(BaseStrategy):
    """
    Advanced Grid Trading Strategy with Telegram signal support
    
    Combines automated grid trading with manual signal following:
    - Mode 1: Auto Grid (ATR-based, self-managing)
    - Mode 2: Signal Following (Telegram signals with grid entry/exit)
    
    Safety features:
    - Max 5x leverage
    - Emergency stop loss
    - Position size limits
    - Partial profit taking
    """
    
    def __init__(self, config: dict):
        """
        Initialize Advanced Grid Bot.
        
        Args:
            config: Configuration dictionary with all parameters
        """
        super().__init__('AdvancedGridBot', config)
        
        # Mode selection
        self.mode = config.get('mode', 'auto')  # 'auto' or 'signal'
        
        # Grid parameters (from NEW bot)
        self.grid_levels = config.get('grid_levels', 10)
        self.grid_spacing_pct = config.get('grid_spacing_pct', 1.0)
        self.upper_price = config.get('upper_price')
        self.lower_price = config.get('lower_price')
        self.initial_capital = config.get('initial_capital', 1000)
        self.rebalance_threshold = config.get('rebalance_threshold', 5.0)
        
        # Trading parameters (from OLD bot)
        self.leverage = min(config.get('leverage', 3), 5)  # Cap at 5x
        self.risk_per_trade_percent = config.get('risk_per_trade_percent', 2.0)
        self.stop_loss_pct = config.get('stop_loss_pct', 15.0)
        
        # TP levels (from OLD bot)
        self.tp_percentages = config.get('tp_percentages', [1.0, 2.0, 3.0, 5.0, 8.0])
        self.tp_position_pct = config.get('tp_position_pct', 20.0)  # 20% per TP
        
        # Grid state
        self.grid_orders = []
        self.filled_orders = []
        self.current_grid = None
        self.base_price = None
        
        # Active positions (from OLD bot)
        self.active_positions = {}
        
        self.logger.info(
            f"Advanced Grid Bot initialized: "
            f"Mode={self.mode}, Leverage={self.leverage}x, "
            f"Grid Levels={self.grid_levels}, Risk={self.risk_per_trade_percent}%"
      )
      # ==================== STRATEGY INTERFACE ====================
    
    def analyze(self, market_data: pd.DataFrame) -> Dict:
        """
        Analyze market data for grid trading.
        
        Args:
            market_data: DataFrame with OHLCV data
            
        Returns:
            Analysis results with price levels and grid status
        """
        if market_data.empty:
            return {'error': 'Empty market data'}
        
        current_price = float(market_data['close'].iloc[-1])
        
        # Calculate price range if not specified
        if self.upper_price is None or self.lower_price is None:
            self._calculate_price_range(market_data)
        
        # Check if grid needs rebalancing
        needs_rebalance = self._check_rebalance_needed(current_price)
        
        # Calculate grid levels
        grid_levels = self._calculate_grid_levels()
        
        # Analyze volatility
        volatility = self._calculate_volatility(market_data)
        
        # Calculate potential profit per grid
        profit_per_grid = (self.grid_spacing_pct / 100) * current_price
        
        # Monitor active positions
        position_status = self._monitor_active_positions(current_price)
        
        analysis = {
            'current_price': current_price,
            'upper_price': self.upper_price,
            'lower_price': self.lower_price,
            'grid_levels': grid_levels,
            'needs_rebalance': needs_rebalance,
            'volatility': volatility,
            'profit_per_grid': profit_per_grid,
            'active_orders': len(self.grid_orders),
            'filled_orders': len(self.filled_orders),
            'active_positions': len(self.active_positions),
            'position_status': position_status,
            'timestamp': datetime.now()
        }
        
        return analysis
    
    def generate_signals(self, analysis: Dict) -> List[Dict]:
        """Generate grid trading signals based on mode."""
        signals = []
        
        if 'error' in analysis:
            return signals
        
        if self.mode == 'auto':
            signals = self._generate_auto_grid_signals(analysis)
        
        return signals
    
    def _generate_auto_grid_signals(self, analysis: Dict) -> List[Dict]:
        """Generate automatic grid signals"""
        signals = []
        
        current_price = analysis['current_price']
        grid_levels = analysis['grid_levels']
        
        if not self.current_grid or analysis['needs_rebalance']:
            signals.extend(self._initialize_grid(grid_levels, current_price))
        
        signals.extend(self._process_filled_orders(current_price))
        
        return signals
    
    # ==================== SIGNAL FOLLOWING ====================
    
    def process_signal(self, signal_text: str) -> Optional[Dict]:
        """Parse and execute Telegram signal."""
        parsed = self._parse_signal(signal_text)
        
        if not parsed:
            self.logger.warning(f"Failed to parse signal: {signal_text}")
            return None
        
        if not self._validate_signal(parsed):
            self.logger.warning(f"Invalid signal: {parsed}")
            return None
        
        result = self._execute_signal_grid_entry(parsed)
        
        return result
    
    def _parse_signal(self, text: str) -> Optional[Dict]:
        """Parse signal text from Telegram."""
        text = text.upper().strip()
        
        match = re.search(
            r'(BTC|ETH|SOL|BNB|MATIC|AVAX|DOT|LINK|UNI|AAVE|XRP|ADA|DOGE)\s+(LONG|SHORT)',
            text
        )
        
        if match:
            symbol = match.group(1)
            direction = match.group(2).lower()
            
            if '/' not in symbol:
                symbol = f"{symbol}/USDT"
            
            return {
                'symbol': symbol,
                'direction': direction,
                'raw_text': text,
                'confidence': 0.8,
                'timestamp': datetime.now()
            }
        
        match = re.search(r'([A-Z]+/[A-Z]+)\s+(LONG|SHORT)', text)
        
        if match:
            return {
                'symbol': match.group(1),
                'direction': match.group(2).lower(),
                'raw_text': text,
                'confidence': 0.9,
                'timestamp': datetime.now()
            }
        
        return None
    
    def _validate_signal(self, signal: Dict) -> bool:
        """Validate parsed signal"""
        if not signal.get('symbol') or not signal.get('direction'):
            return False
        
        if signal['direction'] not in ['long', 'short']:
            return False
        
        if signal.get('confidence', 0) < 0.5:
            return False
        
        if signal['symbol'] in self.active_positions:
            self.logger.warning(f"Already have position for {signal['symbol']}")
            return False
        
        return True
      def _execute_signal_grid_entry(self, signal: Dict) -> Dict:
        """Execute grid entry based on Telegram signal."""
        symbol = signal['symbol']
        direction = signal['direction']
        
        try:
            current_price = self._get_market_price(symbol)
            
            if not current_price:
                return {'success': False, 'error': 'Could not fetch price'}
            
            position_size_usdt = self.initial_capital * (self.risk_per_trade_percent / 100)
            position_size_usdt *= self.leverage
            
            total_amount = position_size_usdt / current_price
            amount_per_level = total_amount / self.grid_levels
            
            grid_percentages = [0.0, -0.5, -1.0, -1.5, -2.0]
            
            entries = []
            total_cost = 0
            
            for i, pct in enumerate(grid_percentages):
                if direction == 'long':
                    entry_price = current_price * (1 + pct / 100)
                else:
                    entry_price = current_price * (1 - pct / 100)
                
                entries.append({
                    'level': i + 1,
                    'price': entry_price,
                    'amount': amount_per_level,
                    'filled': i == 0
                })
                
                if i == 0:
                    total_cost += amount_per_level * entry_price
            
            avg_entry_price = total_cost / amount_per_level
            
            if direction == 'long':
                stop_loss_price = avg_entry_price * (1 - self.stop_loss_pct / 100)
            else:
                stop_loss_price = avg_entry_price * (1 + self.stop_loss_pct / 100)
            
            tp_levels = self._calculate_tp_levels(avg_entry_price, direction)
            
            self.active_positions[symbol] = {
                'direction': direction,
                'entries': entries,
                'avg_entry_price': avg_entry_price,
                'current_price': current_price,
                'total_amount': total_amount,
                'remaining_amount': total_amount,
                'stop_loss': stop_loss_price,
                'take_profits': tp_levels,
                'filled_levels': 1,
                'closed_levels': 0,
                'pnl': 0.0,
                'timestamp': datetime.now()
            }
            
            self.logger.info(
                f"Signal grid entry: {symbol} {direction.upper()}, "
                f"Entry: ${avg_entry_price:.2f}, SL: ${stop_loss_price:.2f}"
            )
            
            return {
                'success': True,
                'symbol': symbol,
                'direction': direction,
                'avg_entry_price': avg_entry_price,
                'entries': entries,
                'stop_loss': stop_loss_price,
                'take_profits': tp_levels,
                'total_amount': total_amount
            }
        
        except Exception as e:
            self.logger.error(f"Signal grid entry error: {e}")
            return {'success': False, 'error': str(e)}
    
    # ==================== GRID CALCULATION ====================
    
    def _calculate_price_range(self, market_data: pd.DataFrame):
        """Calculate optimal price range using ATR"""
        prices = market_data['close'].values
        current_price = float(prices[-1])
        
        high = market_data['high'].values
        low = market_data['low'].values
        close = market_data['close'].values
        
        tr1 = high - low
        tr2 = np.abs(high - np.roll(close, 1))
        tr3 = np.abs(low - np.roll(close, 1))
        
        tr = np.maximum(tr1, np.maximum(tr2, tr3))
        atr = np.mean(tr[-14:])
        
        range_multiplier = 3.0
        price_range = atr * range_multiplier
        
        self.upper_price = current_price + price_range
        self.lower_price = current_price - price_range
        self.base_price = current_price
    
    def _calculate_grid_levels(self) -> List[float]:
        """Calculate price levels for grid"""
        if self.upper_price is None or self.lower_price is None:
            return []
        
        price_range = self.upper_price - self.lower_price
        level_spacing = price_range / (self.grid_levels - 1)
        
        levels = [
            self.lower_price + (i * level_spacing)
            for i in range(self.grid_levels)
        ]
        
        return levels
    
    def _calculate_volatility(self, market_data: pd.DataFrame) -> float:
        """Calculate current market volatility"""
        returns = market_data['close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(24)
        return float(volatility * 100)
    
    def _check_rebalance_needed(self, current_price: float) -> bool:
        """Check if grid needs rebalancing"""
        if self.base_price is None:
            return True
        
        price_change_pct = abs(
            (current_price - self.base_price) / self.base_price * 100
        )
        
        return price_change_pct >= self.rebalance_threshold
    
    def _initialize_grid(self, grid_levels: List[float], current_price: float) -> List[Dict]:
        """Initialize grid orders"""
        signals = []
        capital_per_level = self.initial_capital / (self.grid_levels / 2)
        
        for level in grid_levels:
            if level < current_price:
                order_size = capital_per_level / level
                signals.append({
                    'side': 'buy',
                    'price': level,
                    'amount': order_size,
                    'type': 'limit',
                    'symbol': self.config.get('symbol', 'BTC/USDT'),
                    'grid_level': level
                })
            elif level > current_price:
                order_size = capital_per_level / level
                signals.append({
                    'side': 'sell',
                    'price': level,
                    'amount': order_size,
                    'type': 'limit',
                    'symbol': self.config.get('symbol', 'BTC/USDT'),
                    'grid_level': level
                })
        
        self.current_grid = grid_levels
        self.base_price = current_price
        
        return signals
    
    def _process_filled_orders(self, current_price: float) -> List[Dict]:
        """Process filled orders and create counter orders"""
        return []
    
    def _calculate_tp_levels(self, entry_price: float, direction: str) -> List[Dict]:
        """Calculate take profit levels"""
        tp_levels = []
        
        for i, pct in enumerate(self.tp_percentages):
            if direction == 'long':
                tp_price = entry_price * (1 + pct / 100)
            else:
                tp_price = entry_price * (1 - pct / 100)
            
            tp_levels.append({
                'level': i + 1,
                'price': tp_price,
                'percentage': self.tp_position_pct,
                'target_pct': pct,
                'filled': False
            })
        
        return tp_levels
      def _monitor_active_positions(self, current_price: float) -> List[Dict]:
        """Monitor positions and execute TP/SL"""
        results = []
        
        for symbol, position in list(self.active_positions.items()):
            position['current_price'] = current_price
            
            entry_price = position['avg_entry_price']
            amount = position['remaining_amount']
            direction = position['direction']
            
            if direction == 'long':
                position['pnl'] = (current_price - entry_price) * amount
            else:
                position['pnl'] = (entry_price - current_price) * amount
            
            if self._check_stop_loss(symbol, position):
                result = self._execute_stop_loss(symbol, position)
                results.append(result)
                continue
            
            tp_result = self._check_take_profits(symbol, position)
            if tp_result:
                results.append(tp_result)
        
        return results
    
    def _check_stop_loss(self, symbol: str, position: Dict) -> bool:
        """Check if stop loss hit"""
        current_price = position['current_price']
        stop_loss = position['stop_loss']
        direction = position['direction']
        
        if direction == 'long':
            return current_price <= stop_loss
        else:
            return current_price >= stop_loss
    
    def _execute_stop_loss(self, symbol: str, position: Dict) -> Dict:
        """Execute stop loss - close entire position"""
        current_price = position['current_price']
        pnl = position['pnl']
        
        del self.active_positions[symbol]
        
        trade_info = {
            'symbol': symbol,
            'pnl': pnl,
            'type': 'stop_loss'
        }
        self.update_performance(trade_info)
        
        self.logger.warning(
            f"STOP LOSS: {symbol}, "
            f"Entry: ${position['avg_entry_price']:.2f}, "
            f"Exit: ${current_price:.2f}, P&L: ${pnl:.2f}"
        )
        
        return {
            'type': 'stop_loss',
            'symbol': symbol,
            'pnl': pnl,
            'entry_price': position['avg_entry_price'],
            'exit_price': current_price
        }
    
    def _check_take_profits(self, symbol: str, position: Dict) -> Optional[Dict]:
        """Check and execute take profit levels"""
        current_price = position['current_price']
        direction = position['direction']
        tp_levels = position['take_profits']
        
        for tp in tp_levels:
            if tp['filled']:
                continue
            
            tp_hit = False
            
            if direction == 'long':
                tp_hit = current_price >= tp['price']
            else:
                tp_hit = current_price <= tp['price']
            
            if tp_hit:
                close_amount = position['total_amount'] * (tp['percentage'] / 100)
                
                tp['filled'] = True
                position['closed_levels'] += 1
                position['remaining_amount'] -= close_amount
                
                entry_price = position['avg_entry_price']
                
                if direction == 'long':
                    level_pnl = (current_price - entry_price) * close_amount
                else:
                    level_pnl = (entry_price - current_price) * close_amount
                
                self.logger.info(
                    f"TP{tp['level']} HIT: {symbol}, "
                    f"Price: ${current_price:.2f}, P&L: ${level_pnl:.2f}"
                )
                
                trade_info = {
                    'symbol': symbol,
                    'pnl': level_pnl,
                    'type': 'take_profit'
                }
                self.update_performance(trade_info)
                
                if position['closed_levels'] >= len(tp_levels):
                    del self.active_positions[symbol]
                    self.logger.info(f"Position fully closed: {symbol}")
                
                return {
                    'type': 'take_profit',
                    'symbol': symbol,
                    'level': tp['level'],
                    'pnl': level_pnl,
                    'exit_price': current_price,
                    'target_pct': tp['target_pct']
                }
        
        return None
    
    def _get_market_price(self, symbol: str) -> Optional[float]:
        """Get current market price (placeholder)"""
        default_prices = {
            'BTC/USDT': 43000.0,
            'ETH/USDT': 2300.0,
            'SOL/USDT': 100.0,
            'BNB/USDT': 310.0,
            'XRP/USDT': 0.60,
            'ADA/USDT': 0.50
        }
        return default_prices.get(symbol)
    
    def get_grid_status(self) -> Dict:
        """Get current grid and position status"""
        total_pnl = sum(
            pos['pnl'] for pos in self.active_positions.values()
        )
        
        return {
            'strategy': self.name,
            'mode': self.mode,
            'grid_levels': self.grid_levels,
            'upper_price': self.upper_price,
            'lower_price': self.lower_price,
            'base_price': self.base_price,
            'active_orders': len(self.grid_orders),
            'active_positions': len(self.active_positions),
            'total_unrealized_pnl': total_pnl,
            'leverage': self.leverage,
            'is_active': self.is_active,
            'performance': self.get_performance_summary()
        }
    
    def close_all_positions(self) -> List[Dict]:
        """Emergency close all positions"""
        results = []
        
        for symbol in list(self.active_positions.keys()):
            position = self.active_positions[symbol]
            result = self._execute_stop_loss(symbol, position)
            results.append(result)
        
        self.logger.warning(f"Emergency close: {len(results)} positions closed")
        return results
