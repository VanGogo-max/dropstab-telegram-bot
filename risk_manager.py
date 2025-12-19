# risk_manager.py - Risk Management System
from typing import Dict, Optional
from decimal import Decimal
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class RiskManager:
    """Conservative risk management for safe trading"""
    
    def __init__(self, config: Dict):
        # Risk limits
        self.max_position_size = config.get('max_position_size', 0.1)  # 10% of balance
        self.max_daily_loss = config.get('max_daily_loss', 0.05)  # 5% daily loss limit
        self.max_drawdown = config.get('max_drawdown', 0.10)  # 10% max drawdown
        self.max_leverage = config.get('max_leverage', 3)  # Max 3x leverage
        
        # Trading limits
        self.max_open_positions = config.get('max_open_positions', 5)
        self.min_profit_target = config.get('min_profit_target', 0.02)  # 2% min profit
        self.stop_loss_percent = config.get('stop_loss_percent', 0.03)  # 3% stop loss
        
        # State tracking
        self.daily_pnl = 0
        self.peak_balance = 0
        self.daily_trades = 0
        self.last_reset = datetime.now()
        self.emergency_stop = False
    
    def reset_daily_stats(self):
        """Reset daily statistics"""
        now = datetime.now()
        if now.date() > self.last_reset.date():
            self.daily_pnl = 0
            self.daily_trades = 0
            self.last_reset = now
            logger.info("Daily stats reset")
    
    def check_daily_loss_limit(self, current_balance: float) -> bool:
        """Check if daily loss limit exceeded"""
        self.reset_daily_stats()
        
        if self.peak_balance == 0:
            self.peak_balance = current_balance
        
        daily_loss = (self.peak_balance - current_balance) / self.peak_balance
        
        if daily_loss >= self.max_daily_loss:
            logger.warning(f"Daily loss limit reached: {daily_loss:.2%}")
            self.emergency_stop = True
            return False
        return True
    
    def check_drawdown(self, current_balance: float, initial_balance: float) -> bool:
        """Check maximum drawdown"""
        if initial_balance == 0:
            return True
        
        drawdown = (initial_balance - current_balance) / initial_balance
        
        if drawdown >= self.max_drawdown:
            logger.warning(f"Max drawdown reached: {drawdown:.2%}")
            self.emergency_stop = True
            return False
        return True
    
    def calculate_position_size(self, balance: float, risk_percent: float = None) -> float:
        """Calculate safe position size"""
        if risk_percent is None:
            risk_percent = self.max_position_size
        
        position_size = balance * min(risk_percent, self.max_position_size)
        logger.info(f"Calculated position size: ${position_size:.2f}")
        return position_size
    
    def validate_order(self, order: Dict, balance: float, open_positions: int) -> Dict:
        """Validate order before execution"""
        errors = []
        
        # Check emergency stop
        if self.emergency_stop:
            errors.append("Emergency stop active")
            return {'valid': False, 'errors': errors}
        
        # Check position count
        if open_positions >= self.max_open_positions:
            errors.append(f"Max positions reached ({self.max_open_positions})")
        
        # Check position size
        order_value = order.get('amount', 0) * order.get('price', 0)
        if order_value > balance * self.max_position_size:
            errors.append(f"Position too large (max {self.max_position_size:.0%} of balance)")
        
        # Check leverage
        leverage = order.get('leverage', 1)
        if leverage > self.max_leverage:
            errors.append(f"Leverage too high (max {self.max_leverage}x)")
        
        # Check minimum amount
        if order_value < 10:  # Minimum $10 order
            errors.append("Order value too small (min $10)")
        
        if errors:
            logger.warning(f"Order validation failed: {errors}")
            return {'valid': False, 'errors': errors}
        
        return {'valid': True, 'errors': []}
    
    def calculate_stop_loss(self, entry_price: float, side: str) -> float:
        """Calculate stop loss price"""
        if side == 'buy':
            stop_loss = entry_price * (1 - self.stop_loss_percent)
        else:
            stop_loss = entry_price * (1 + self.stop_loss_percent)
        
        return round(stop_loss, 8)
    
    def calculate_take_profit(self, entry_price: float, side: str, 
                             profit_target: float = None) -> float:
        """Calculate take profit price"""
        if profit_target is None:
            profit_target = self.min_profit_target
        
        if side == 'buy':
            take_profit = entry_price * (1 + profit_target)
        else:
            take_profit = entry_price * (1 - profit_target)
        
        return round(take_profit, 8)
    
    def update_pnl(self, pnl: float):
        """Update daily P&L"""
        self.daily_pnl += pnl
        logger.info(f"Daily P&L: ${self.daily_pnl:.2f}")
    
    def should_reduce_risk(self, consecutive_losses: int) -> bool:
        """Check if risk should be reduced"""
        if consecutive_losses >= 3:
            logger.warning(f"Consecutive losses: {consecutive_losses}, reducing risk")
            return True
        return False
    
    def get_risk_score(self, balance: float, initial_balance: float, 
                       volatility: float) -> Dict:
        """Calculate overall risk score"""
        # Drawdown risk
        drawdown = (initial_balance - balance) / initial_balance if initial_balance > 0 else 0
        drawdown_risk = min(drawdown / self.max_drawdown, 1.0)
        
        # Daily loss risk
        daily_loss = abs(self.daily_pnl) / balance if balance > 0 else 0
        daily_risk = min(daily_loss / self.max_daily_loss, 1.0)
        
        # Volatility risk (0-1 scale)
        volatility_risk = min(volatility / 0.5, 1.0)  # 50% volatility = max risk
        
        # Overall risk (weighted average)
        total_risk = (drawdown_risk * 0.4 + daily_risk * 0.3 + volatility_risk * 0.3)
        
        risk_level = 'LOW' if total_risk < 0.3 else 'MEDIUM' if total_risk < 0.7 else 'HIGH'
        
        return {
            'score': total_risk,
            'level': risk_level,
            'drawdown_risk': drawdown_risk,
            'daily_risk': daily_risk,
            'volatility_risk': volatility_risk,
            'recommendation': self._get_recommendation(total_risk)
        }
    
    def _get_recommendation(self, risk_score: float) -> str:
        """Get risk-based recommendation"""
        if risk_score < 0.3:
            return "Normal trading allowed"
        elif risk_score < 0.5:
            return "Reduce position sizes by 30%"
        elif risk_score < 0.7:
            return "Reduce position sizes by 50%"
        else:
            return "Stop trading and review strategy"
    
    def reset_emergency_stop(self):
        """Reset emergency stop (manual intervention)"""
        self.emergency_stop = False
        logger.info("Emergency stop reset")
    
    def get_status(self) -> Dict:
        """Get current risk status"""
        return {
            'emergency_stop': self.emergency_stop,
            'daily_pnl': self.daily_pnl,
            'daily_trades': self.daily_trades,
            'peak_balance': self.peak_balance,
            'max_positions': self.max_open_positions,
            'max_daily_loss': self.max_daily_loss,
            'max_drawdown': self.max_drawdown
        }
