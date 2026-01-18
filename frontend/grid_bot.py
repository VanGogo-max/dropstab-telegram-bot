"""Grid Trading Strategy Implementation."""

import logging
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime

from base_strategy import BaseStrategy


class GridTradingStrategy(BaseStrategy):
    """
    Grid Trading Strategy - Places buy and sell orders at predetermined intervals.
    
    The strategy creates a grid of orders above and below the current price,
    profiting from market oscillations within the grid range.
    """
    
    def __init__(self, config: dict):
        """
        Initialize Grid Trading Strategy.
        
        Args:
            config: Strategy configuration
        """
        super().__init__('GridTrading', config)
        
        # Grid parameters
        self.grid_levels = config.get('grid_levels', 10)
        self.grid_spacing_pct = config.get('grid_spacing_pct', 1.0)
        self.upper_price = config.get('upper_price')
        self.lower_price = config.get('lower_price')
        self.initial_capital = config.get('initial_capital', 1000)
        self.rebalance_threshold = config.get('rebalance_threshold', 5.0)
        
        # Grid state
        self.grid_orders = []
        self.filled_orders = []
        self.current_grid = None
        self.base_price = None
        
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
            'timestamp': datetime.now()
        }
        
        return analysis
        
    def generate_signals(self, analysis: Dict) -> List[Dict]:
        """
        Generate grid trading signals.
        
        Args:
            analysis: Analysis results from analyze()
            
        Returns:
            List of trading signals
        """
        signals = []
        
        if 'error' in analysis:
            return signals
            
        current_price = analysis['current_price']
        grid_levels = analysis['grid_levels']
        
        # Initialize grid if not exists or needs rebalance
        if not self.current_grid or analysis['needs_rebalance']:
            signals.extend(self._initialize_grid(grid_levels, current_price))
            
        # Check for filled orders and create counter orders
        signals.extend(self._process_filled_orders(current_price))
        
        return signals
        
    def _calculate_price_range(self, market_data: pd.DataFrame):
        """
        Calculate optimal price range for grid based on historical data.
        
        Args:
            market_data: Historical price data
        """
        prices = market_data['close'].values
        current_price = float(prices[-1])
        
        # Use ATR (Average True Range) for dynamic range
        high = market_data['high'].values
        low = market_data['low'].values
        close = market_data['close'].values
        
        tr1 = high - low
        tr2 = np.abs(high - np.roll(close, 1))
        tr3 = np.abs(low - np.roll(close, 1))
        
        tr = np.maximum(tr1, np.maximum(tr2, tr3))
        atr = np.mean(tr[-14:])  # 14-period ATR
        
        # Set range based on ATR and volatility
        range_multiplier = 3.0  # 3x ATR for range
        price_range = atr * range_multiplier
        
        self.upper_price = current_price + price_range
        self.lower_price = current_price - price_range
        self.base_price = current_price
        
        self.logger.info(f"Price range calculated: {self.lower_price:.2f} - {self.upper_price:.2f}")
        
    def _calculate_grid_levels(self) -> List[float]:
        """
        Calculate price levels for grid orders.
        
        Returns:
            List of price levels
        """
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
        """
        Calculate current market volatility.
        
        Args:
            market_data: Historical price data
            
        Returns:
            Volatility percentage
        """
        returns = market_data['close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(24)  # Annualized for hourly data
        return float(volatility * 100)
        
    def _check_rebalance_needed(self, current_price: float) -> bool:
        """
        Check if grid needs rebalancing.
        
        Args:
            current_price: Current market price
            
        Returns:
            True if rebalancing needed
        """
        if self.base_price is None:
            return True
            
        price_change_pct = abs(
            (current_price - self.base_price) / self.base_price * 100
        )
        
        return price_change_pct >= self.rebalance_threshold
        
    def _initialize_grid(self, grid_levels: List[float], current_price: float) -> List[Dict]:
        """
        Initialize grid orders.
        
        Args:
            grid_levels: List of price levels
            current_price: Current market price
            
        Returns:
            List of initial grid signals
        """
        signals = []
        
        # Calculate order size per grid level
        capital_per_level = self.initial_capital / (self.grid_levels / 2)
        
        for level in grid_levels:
            if level < current_price:
                # Place buy orders below current price
                order_size = capital_per_level / level
                signals.append({
                    'side': 'buy',
                    'price': level,
                    'amount': order_size,
                    'type': 'limit',
                    'symbol': self.config.get('symbol', 'BTC/USDT'),
                    'grid_level': level,
                    'timestamp': datetime.now()
                })
            elif level > current_price:
                # Place sell orders above current price
                order_size = capital_per_level / level
                signals.append({
                    'side': 'sell',
                    'price': level,
                    'amount': order_size,
                    'type': 'limit',
                    'symbol': self.config.get('symbol', 'BTC/USDT'),
                    'grid_level': level,
                    'timestamp': datetime.now()
                })
                
        self.current_grid = grid_levels
        self.base_price = current_price
        
        self.logger.info(f"Grid initialized with {len(signals)} orders")
        return signals
        
    def _process_filled_orders(self, current_price: float) -> List[Dict]:
        """
        Process filled orders and create counter orders.
        
        Args:
            current_price: Current market price
            
        Returns:
            List of counter order signals
        """
        signals = []
        
        # This would be called when orders are filled
        # For now, returns empty list
        # In real implementation, would check exchange for filled orders
        # and create opposite orders at next grid level
        
        return signals
        
    def on_order_filled(self, order: Dict):
        """
        Handle filled order event.
        
        Args:
            order: Filled order information
        """
        self.filled_orders.append(order)
        
        # Create counter order at next grid level
        if order['side'] == 'buy':
            # Filled buy order, create sell order above
            next_level = order['price'] * (1 + self.grid_spacing_pct / 100)
            counter_signal = {
                'side': 'sell',
                'price': next_level,
                'amount': order['amount'],
                'type': 'limit',
                'symbol': order['symbol'],
                'grid_level': next_level,
                'timestamp': datetime.now()
            }
        else:
            # Filled sell order, create buy order below
            next_level = order['price'] * (1 - self.grid_spacing_pct / 100)
            counter_signal = {
                'side': 'buy',
                'price': next_level,
                'amount': order['amount'],
                'type': 'limit',
                'symbol': order['symbol'],
                'grid_level': next_level,
                'timestamp': datetime.now()
            }
            
        self.logger.info(f"Counter order created at {next_level:.2f}")
        return counter_signal
        
    def get_grid_status(self) -> Dict:
        """
        Get current grid status and statistics.
        
        Returns:
            Grid status information
        """
        total_profit = sum(
            order.get('profit', 0) for order in self.filled_orders
        )
        
        return {
            'strategy': self.name,
            'grid_levels': self.grid_levels,
            'upper_price': self.upper_price,
            'lower_price': self.lower_price,
            'base_price': self.base_price,
            'active_orders': len(self.grid_orders),
            'filled_orders': len(self.filled_orders),
            'total_profit': total_profit,
            'grid_spacing': self.grid_spacing_pct,
            'is_active': self.is_active
        }
        
    def reset_grid(self):
        """Reset grid state."""
        self.grid_orders = []
        self.filled_orders = []
        self.current_grid = None
        self.base_price = None
        self.logger.info("Grid reset completed")


# Example usage
if __name__ == '__main__':
    # Example configuration
    config = {
        'symbol': 'BTC/USDT',
        'grid_levels': 10,
        'grid_spacing_pct': 1.0,
        'initial_capital': 1000,
        'rebalance_threshold': 5.0
    }
    
    # Create strategy instance
    grid_strategy = GridTradingStrategy(config)
    
    # Create sample market data
    dates = pd.date_range('2024-01-01', periods=100, freq='1h')
    data = pd.DataFrame({
        'timestamp': dates,
        'open': np.random.uniform(40000, 42000, 100),
        'high': np.random.uniform(40000, 42000, 100),
        'low': np.random.uniform(40000, 42000, 100),
        'close': np.random.uniform(40000, 42000, 100),
        'volume': np.random.uniform(100, 1000, 100)
    })
    
    # Run analysis
    analysis = grid_strategy.analyze(data)
    print("\n📊 Grid Analysis:")
    print(f"Current Price: ${analysis['current_price']:.2f}")
    print(f"Grid Range: ${analysis['lower_price']:.2f} - ${analysis['upper_price']:.2f}")
    print(f"Grid Levels: {len(analysis['grid_levels'])}")
    print(f"Profit per Grid: ${analysis['profit_per_grid']:.2f}")
    
    # Generate signals
    signals = grid_strategy.generate_signals(analysis)
    print(f"\n📈 Generated {len(signals)} grid orders")
    
    # Show grid status
    status = grid_strategy.get_grid_status()
    print("\n✅ Grid Status:")
    for key, value in status.items():
        print(f"{key}: {value}")
