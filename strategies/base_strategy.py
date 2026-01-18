"""Base strategy class for all trading strategies."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import pandas as pd
import logging
from datetime import datetime


class BaseStrategy(ABC):
    """Abstract base class for trading strategies."""
    
    def __init__(self, name: str, config: dict):
        """Initialize base strategy."""
        self.name = name
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{name}")
        
        self.is_active = False
        self.positions = {}
        self.orders = []
        self.performance = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0.0,
            'sharpe_ratio': 0.0
        }
        
    @abstractmethod
    def analyze(self, market_data: pd.DataFrame) -> Dict:
        """Analyze market data and generate signals."""
        pass
        
    @abstractmethod
    def generate_signals(self, analysis: Dict) -> List[Dict]:
        """Generate trading signals based on analysis."""
        pass
        
    def validate_signal(self, signal: Dict) -> bool:
        """Validate trading signal."""
        required_fields = ['side', 'symbol', 'amount']
        return all(field in signal for field in required_fields)
        
    def calculate_position_size(self, signal: Dict, balance: float, risk_pct: float) -> float:
        """Calculate position size based on risk parameters."""
        risk_amount = balance * (risk_pct / 100)
        price = signal.get('price', 0)
        
        if price <= 0:
            return 0.0
            
        return risk_amount / price
        
    def update_performance(self, trade: Dict):
        """Update strategy performance metrics."""
        self.performance['total_trades'] += 1
        
        pnl = trade.get('pnl', 0)
        self.performance['total_pnl'] += pnl
        
        if pnl > 0:
            self.performance['winning_trades'] += 1
        elif pnl < 0:
            self.performance['losing_trades'] += 1
            
    def get_performance_summary(self) -> Dict:
        """Get strategy performance summary."""
        total = self.performance['total_trades']
        if total > 0:
            win_rate = (self.performance['winning_trades'] / total) * 100
        else:
            win_rate = 0.0
            
        return {
            'name': self.name,
            'total_trades': total,
            'winning_trades': self.performance['winning_trades'],
            'losing_trades': self.performance['losing_trades'],
            'win_rate': win_rate,
            'total_pnl': self.performance['total_pnl'],
            'sharpe_ratio': self.performance['sharpe_ratio']
        }
        
    def reset_performance(self):
        """Reset performance metrics."""
        self.performance = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0.0,
            'sharpe_ratio': 0.0
        }
        
    def activate(self):
        """Activate strategy."""
        self.is_active = True
        self.logger.info(f"Strategy {self.name} activated")
        
    def deactivate(self):
        """Deactivate strategy."""
        self.is_active = False
        self.logger.info(f"Strategy {self.name} deactivated")
        
    def get_config(self) -> Dict:
        """Get strategy configuration."""
        return self.config.copy()
        
    def update_config(self, new_config: Dict):
        """Update strategy configuration."""
        self.config.update(new_config)
        self.logger.info(f"Strategy {self.name} configuration updated")
Кажи "Готово" 🚀
