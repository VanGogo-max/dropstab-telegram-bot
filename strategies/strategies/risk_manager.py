"""Risk management system for trading bot."""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class RiskManager:
    """Manages trading risk and position limits."""
    
    def __init__(self, config: dict):
        """Initialize risk manager with configuration."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        self.max_position_size_pct = config.get('max_position_size_pct', 10.0)
        self.max_total_exposure_pct = config.get('max_total_exposure_pct', 50.0)
        self.max_daily_loss_pct = config.get('max_daily_loss_pct', 5.0)
        self.max_drawdown_pct = config.get('max_drawdown_pct', 15.0)
        self.max_open_positions = config.get('max_open_positions', 5)
        
        self.daily_pnl = 0.0
        self.daily_start_balance = 0.0
        self.peak_balance = 0.0
        self.open_positions = []
        self.daily_reset_time = datetime.now().replace(hour=0, minute=0, second=0)
        
        self.logger.info("Risk Manager initialized with limits:")
        self.logger.info(f"  Max position size: {self.max_position_size_pct}%")
        self.logger.info(f"  Max total exposure: {self.max_total_exposure_pct}%")
        self.logger.info(f"  Max daily loss: {self.max_daily_loss_pct}%")
        
    def check_signal(self, signal: Dict, current_balance: float) -> Dict:
        """Check if signal passes risk management rules."""
        if self._should_reset_daily_stats():
            self._reset_daily_stats(current_balance)
        
        checks = {
            'approved': True,
            'reasons': [],
            'adjusted_size': signal.get('amount', 0)
        }
        
        if not self._check_daily_loss_limit(current_balance):
            checks['approved'] = False
            checks['reasons'].append('Daily loss limit reached')
            return checks
        
        if not self._check_max_positions():
            checks['approved'] = False
            checks['reasons'].append('Maximum open positions reached')
            return checks
        
        if not self._check_position_size(signal, current_balance):
            checks['approved'] = False
            checks['reasons'].append('Position size exceeds limit')
            return checks
        
        if not self._check_total_exposure(signal, current_balance):
            adjusted = self._adjust_position_size(signal, current_balance)
            if adjusted:
                checks['adjusted_size'] = adjusted
                checks['reasons'].append('Position size adjusted for exposure')
            else:
                checks['approved'] = False
                checks['reasons'].append('Total exposure limit reached')
                return checks
        
        return checks
    
    def _check_daily_loss_limit(self, current_balance: float) -> bool:
        """Check if daily loss limit is reached."""
        if self.daily_start_balance == 0:
            return True
        
        loss_pct = (self.daily_pnl / self.daily_start_balance) * 100
        
        if loss_pct <= -self.max_daily_loss_pct:
            self.logger.warning(f"Daily loss limit reached: {loss_pct:.2f}%")
            return False
        
        return True
    
    def _check_max_positions(self) -> bool:
        """Check if maximum open positions is reached."""
        if len(self.open_positions) >= self.max_open_positions:
            self.logger.warning(f"Max positions reached: {len(self.open_positions)}")
            return False
        return True
    
    def _check_position_size(self, signal: Dict, balance: float) -> bool:
        """Check if position size is within limits."""
        amount = signal.get('amount', 0)
        price = signal.get('price', 0)
        
        if price == 0:
            return False
        
        position_value = amount * price
        position_pct = (position_value / balance) * 100
        
        if position_pct > self.max_position_size_pct:
            self.logger.warning(f"Position too large: {position_pct:.2f}%")
            return False
        
        return True
    
    def _check_total_exposure(self, signal: Dict, balance: float) -> bool:
        """Check if total exposure is within limits."""
        amount = signal.get('amount', 0)
        price = signal.get('price', 0)
        
        new_position_value = amount * price
        current_exposure = sum(p.get('value', 0) for p in self.open_positions)
        total_exposure = current_exposure + new_position_value
        
        exposure_pct = (total_exposure / balance) * 100
        
        if exposure_pct > self.max_total_exposure_pct:
            self.logger.warning(f"Total exposure too high: {exposure_pct:.2f}%")
            return False
        
        return True
    
    def _adjust_position_size(self, signal: Dict, balance: float) -> Optional[float]:
        """Adjust position size to fit within exposure limits."""
        price = signal.get('price', 0)
        if price == 0:
            return None
        
        current_exposure = sum(p.get('value', 0) for p in self.open_positions)
        available_exposure = (balance * self.max_total_exposure_pct / 100) - current_exposure
        
        if available_exposure <= 0:
            return None
        
        max_amount = available_exposure / price
        return max_amount
    
    def update_position(self, position: Dict):
        """Update open position tracking."""
        self.open_positions.append(position)
        self.logger.info(f"Position added: {position.get('symbol', 'Unknown')}")
    
    def close_position(self, position_id: str, pnl: float):
        """Remove closed position and update P&L."""
        self.open_positions = [p for p in self.open_positions if p.get('id') != position_id]
        self.daily_pnl += pnl
        self.logger.info(f"Position closed. Daily P&L: ${self.daily_pnl:.2f}")
    
    def _should_reset_daily_stats(self) -> bool:
        """Check if daily stats should be reset."""
        now = datetime.now()
        return now >= self.daily_reset_time + timedelta(days=1)
    
    def _reset_daily_stats(self, current_balance: float):
        """Reset daily statistics."""
        self.daily_pnl = 0.0
        self.daily_start_balance = current_balance
        self.daily_reset_time = datetime.now().replace(hour=0, minute=0, second=0)
        self.logger.info("Daily stats reset")
    
    def get_risk_status(self) -> Dict:
        """Get current risk management status."""
        return {
            'open_positions': len(self.open_positions),
            'max_positions': self.max_open_positions,
            'daily_pnl': self.daily_pnl,
            'daily_start_balance': self.daily_start_balance,
            'positions': self.open_positions
