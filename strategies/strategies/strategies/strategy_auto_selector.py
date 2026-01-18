"""Automatic strategy selector based on market conditions and performance."""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class StrategyAutoSelector:
    """Automatically selects best performing strategy based on conditions."""
    
    def __init__(self):
        """Initialize strategy auto selector."""
        self.logger = logging.getLogger(__name__)
        self.registered_strategies = {}
        self.active_strategy = None
        self.performance_history = {}
        
        self.logger.info("Strategy Auto Selector initialized")
    
    def register_strategy(self, strategy) -> bool:
        """Register a strategy for selection."""
        try:
            strategy_name = strategy.name
            self.registered_strategies[strategy_name] = strategy
            self.performance_history[strategy_name] = []
            
            self.logger.info(f"Strategy registered: {strategy_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register strategy: {e}")
            return False
    
    def select_best_strategy(self, market_conditions: Dict) -> Optional[str]:
        """Select best strategy based on performance and market conditions."""
        if not self.registered_strategies:
            self.logger.warning("No strategies registered")
            return None
        
        scores = {}
        
        for name, strategy in self.registered_strategies.items():
            score = self._calculate_strategy_score(strategy, market_conditions)
            scores[name] = score
            self.logger.debug(f"Strategy {name} score: {score:.2f}")
        
        best_strategy = max(scores, key=scores.get)
        best_score = scores[best_strategy]
        
        if best_score > 0:
            self.logger.info(f"Best strategy selected: {best_strategy} (score: {best_score:.2f})")
            self.active_strategy = best_strategy
            return best_strategy
        else:
            self.logger.warning("No suitable strategy found")
            return None
    
    def _calculate_strategy_score(self, strategy, market_conditions: Dict) -> float:
        """Calculate overall score for a strategy."""
        performance_score = self._get_performance_score(strategy)
        market_fit_score = self._get_market_fit_score(strategy, market_conditions)
        risk_score = self._get_risk_score(strategy)
        
        total_score = (
            performance_score * 0.5 +
            market_fit_score * 0.3 +
            risk_score * 0.2
        )
        
        return total_score
    
    def _get_performance_score(self, strategy) -> float:
        """Calculate performance score based on historical results."""
        perf = strategy.get_performance_summary()
        
        total_trades = perf.get('total_trades', 0)
        if total_trades == 0:
            return 0.5
        
        win_rate = perf.get('win_rate', 0)
        total_pnl = perf.get('total_pnl', 0)
        
        win_rate_score = win_rate / 100
        pnl_score = min(max(total_pnl / 1000, 0), 1)
        
        return (win_rate_score * 0.6 + pnl_score * 0.4)
    
    def _get_market_fit_score(self, strategy, market_conditions: Dict) -> float:
        """Score how well strategy fits current market conditions."""
        volatility = market_conditions.get('volatility', 0)
        trend_strength = market_conditions.get('trend_strength', 0)
        
        strategy_name = strategy.name.lower()
        
        if 'grid' in strategy_name:
            if volatility < 0.02:
                return 0.8
            elif volatility < 0.05:
                return 0.6
            else:
                return 0.3
        
        elif 'trend' in strategy_name or 'momentum' in strategy_name:
            if trend_strength > 0.7:
                return 0.9
            elif trend_strength > 0.5:
                return 0.6
            else:
                return 0.3
        
        elif 'mean_reversion' in strategy_name:
            if volatility > 0.03 and trend_strength < 0.5:
                return 0.8
            else:
                return 0.4
        
        return 0.5
    
    def _get_risk_score(self, strategy) -> float:
        """Calculate risk score (lower risk = higher score)."""
        perf = strategy.get_performance_summary()
        
        total_trades = perf.get('total_trades', 0)
        losing_trades = perf.get('losing_trades', 0)
        
        if total_trades == 0:
            return 0.5
        
        loss_rate = losing_trades / total_trades
        risk_score = 1.0 - loss_rate
        
        return risk_score
    
    def update_performance(self, strategy_name: str, trade_result: Dict):
        """Update performance history for a strategy."""
        if strategy_name not in self.performance_history:
            return
        
        self.performance_history[strategy_name].append({
            'timestamp': datetime.now(),
            'pnl': trade_result.get('pnl', 0),
            'result': 'win' if trade_result.get('pnl', 0) > 0 else 'loss'
        })
        
        max_history = 100
        if len(self.performance_history[strategy_name]) > max_history:
            self.performance_history[strategy_name] = self.performance_history[strategy_name][-max_history:]
    
    def get_active_strategy(self) -> Optional[str]:
        """Get currently active strategy name."""
        return self.active_strategy
    
    def get_all_strategies(self) -> List[str]:
        """Get list of all registered strategies."""
        return list(self.registered_strategies.keys())
    
    def get_strategy_stats(self) -> Dict:
        """Get statistics for all strategies."""
        stats = {}
        
        for name, strategy in self.registered_strategies.items():
            stats[name] = strategy.get_performance_summary()
        
        return
