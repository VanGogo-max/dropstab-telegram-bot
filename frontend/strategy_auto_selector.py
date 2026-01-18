"""
AI Strategy Auto-Selector
Analyzes market conditions and user profile to recommend best trading strategy

КАЧИ ТОЗИ ФАЙЛ В КОРЕНА НА ПРОЕКТА (до main.py, database.py и т.н.)
"""

import logging
from enum import Enum
from typing import List, Tuple, Dict, Optional
import numpy as np

logger = logging.getLogger(__name__)


class StrategyType(Enum):
    """Available trading strategies"""
    GRID = "grid"
    DCA = "dca"
    LIQUIDITY = "liquidity"
    TURTLE = "turtle"
    ICT = "ict"
    PRICE_ARBITRAGE = "price_arbitrage"
    FUNDING_ARBITRAGE = "funding_arbitrage"
    AGGRESSIVE_SCALPER = "aggressive_scalper"
    MEAN_REVERSION = "mean_reversion"
    TREND_MASTER = "trend_master"


class StrategyAutoSelector:
    """
    Intelligent strategy selector based on:
    - Market conditions (volatility, trend, volume)
    - User profile (capital, experience, risk tolerance)
    """
    
    def __init__(self):
        logger.info("Strategy Auto-Selector initialized")
    
    def recommend_strategy(
        self,
        candles: List[Dict],
        user_profile: Dict,
        top_n: int = 3
    ) -> List[Tuple[StrategyType, float, str]]:
        """
        Recommend top N strategies
        
        Args:
            candles: Market data (OHLCV)
            user_profile: {
                'capital': 5000,
                'experience': 'intermediate',
                'risk_tolerance': 'medium',
                'can_monitor': False
            }
            top_n: Number of recommendations
        
        Returns:
            List of (StrategyType, score, reasoning)
        """
        try:
            # 1. Analyze market
            market_analysis = self._analyze_market(candles)
            
            # 2. Score all strategies
            scores = {}
            
            for strategy in StrategyType:
                score = self._score_strategy(
                    strategy,
                    market_analysis,
                    user_profile
                )
                reasoning = self._generate_reasoning(
                    strategy,
                    market_analysis,
                    user_profile,
                    score
                )
                scores[strategy] = (score, reasoning)
            
            # 3. Sort by score
            sorted_strategies = sorted(
                scores.items(),
                key=lambda x: x[1][0],
                reverse=True
            )
            
            # 4. Return top N
            recommendations = [
                (strategy, score, reasoning)
                for strategy, (score, reasoning) in sorted_strategies[:top_n]
            ]
            
            logger.info(f"Generated {len(recommendations)} strategy recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Strategy recommendation error: {e}")
            # Fallback to safe defaults
            return [
                (StrategyType.DCA, 70.0, "Safe default strategy for all market conditions"),
                (StrategyType.GRID, 60.0, "Good for ranging markets"),
                (StrategyType.TURTLE, 50.0, "Trend following strategy")
            ]
    
    def _analyze_market(self, candles: List[Dict]) -> Dict:
        """Analyze current market conditions"""
        try:
            if not candles or len(candles) < 20:
                logger.warning("Insufficient candle data, using defaults")
                return {
                    'volatility': 'medium',
                    'trend': 'neutral',
                    'volume_trend': 'stable',
                    'atr_percent': 2.0
                }
            
            closes = [c['close'] for c in candles]
            highs = [c['high'] for c in candles]
            lows = [c['low'] for c in candles]
            volumes = [c['volume'] for c in candles]
            
            # Calculate volatility (ATR %)
            atr = self._calculate_atr(highs, lows, closes)
            current_price = closes[-1]
            atr_percent = (atr / current_price) * 100
            
            # Determine volatility level
            if atr_percent < 1.5:
                volatility = 'low'
            elif atr_percent < 3.0:
                volatility = 'medium'
            else:
                volatility = 'high'
            
            # Calculate trend
            sma_20 = np.mean(closes[-20:])
            sma_50 = np.mean(closes[-50:]) if len(closes) >= 50 else sma_20
            
            if current_price > sma_20 > sma_50:
                trend = 'bullish'
            elif current_price < sma_20 < sma_50:
                trend = 'bearish'
            else:
                trend = 'neutral'
            
            # Volume trend
            recent_vol = np.mean(volumes[-10:])
            older_vol = np.mean(volumes[-30:-10]) if len(volumes) >= 30 else recent_vol
            
            if recent_vol > older_vol * 1.2:
                volume_trend = 'increasing'
            elif recent_vol < older_vol * 0.8:
                volume_trend = 'decreasing'
            else:
                volume_trend = 'stable'
            
            analysis = {
                'volatility': volatility,
                'trend': trend,
                'volume_trend': volume_trend,
                'atr_percent': atr_percent,
                'current_price': current_price
            }
            
            logger.info(f"Market analysis: {analysis}")
            return analysis
            
        except Exception as e:
            logger.error(f"Market analysis error: {e}")
            return {
                'volatility': 'medium',
                'trend': 'neutral',
                'volume_trend': 'stable',
                'atr_percent': 2.0
            }
    
    def _calculate_atr(self, highs: List[float], lows: List[float], 
                       closes: List[float], period: int = 14) -> float:
        """Calculate Average True Range"""
        try:
            true_ranges = []
            
            for i in range(1, len(highs)):
                high_low = highs[i] - lows[i]
                high_close = abs(highs[i] - closes[i-1])
                low_close = abs(lows[i] - closes[i-1])
                
                true_range = max(high_low, high_close, low_close)
                true_ranges.append(true_range)
            
            if len(true_ranges) >= period:
                atr = np.mean(true_ranges[-period:])
            else:
                atr = np.mean(true_ranges) if true_ranges else 0
            
            return atr
            
        except Exception as e:
            logger.error(f"ATR calculation error: {e}")
            return 0
    
    def _score_strategy(
        self,
        strategy: StrategyType,
        market: Dict,
        profile: Dict
    ) -> float:
        """Score a strategy (0-100)"""
        score = 50.0  # Base score
        
        capital = profile.get('capital', 1000)
        experience = profile.get('experience', 'beginner')
        risk_tolerance = profile.get('risk_tolerance', 'low')
        can_monitor = profile.get('can_monitor', False)
        
        volatility = market.get('volatility', 'medium')
        trend = market.get('trend', 'neutral')
        
        # ===== GRID STRATEGY =====
        if strategy == StrategyType.GRID:
            if volatility == 'low':
                score += 20
            elif volatility == 'medium':
                score += 10
            
            if trend == 'neutral':
                score += 15
            
            if capital >= 1000:
                score += 10
            
            if experience in ['beginner', 'intermediate']:
                score += 5
        
        # ===== DCA STRATEGY =====
        elif strategy == StrategyType.DCA:
            score += 15
            
            if experience == 'beginner':
                score += 20
            
            if not can_monitor:
                score += 15
            
            if capital >= 500:
                score += 10
        
        # ===== TURTLE STRATEGY =====
        elif strategy == StrategyType.TURTLE:
            if trend in ['bullish', 'bearish']:
                score += 25
            
            if volatility in ['medium', 'high']:
                score += 10
            
            if experience in ['intermediate', 'advanced', 'expert']:
                score += 10
            
            if capital >= 2000:
                score += 5
        
        # ===== AGGRESSIVE SCALPER =====
        elif strategy == StrategyType.AGGRESSIVE_SCALPER:
            if volatility == 'high':
                score += 25
            
            if can_monitor:
                score += 20
            else:
                score -= 30
            
            if experience in ['advanced', 'expert']:
                score += 15
            else:
                score -= 20
            
            if risk_tolerance == 'high':
                score += 10
        
        # ===== MEAN REVERSION =====
        elif strategy == StrategyType.MEAN_REVERSION:
            if volatility == 'low':
                score += 15
            
            if trend == 'neutral':
                score += 20
            
            if experience in ['intermediate', 'advanced']:
                score += 10
        
        # ===== TREND MASTER =====
        elif strategy == StrategyType.TREND_MASTER:
            if trend in ['bullish', 'bearish']:
                score += 30
            
            if volatility in ['medium', 'high']:
                score += 10
            
            if experience in ['intermediate', 'advanced', 'expert']:
                score += 10
        
        # ===== ARBITRAGE =====
        elif strategy == StrategyType.PRICE_ARBITRAGE:
            if capital >= 5000:
                score += 20
            else:
                score -= 20
            
            if experience in ['advanced', 'expert']:
                score += 15
            
            score += 10
        
        # ===== LIQUIDITY =====
        elif strategy == StrategyType.LIQUIDITY:
            if capital >= 3000:
                score += 15
            
            if experience in ['intermediate', 'advanced', 'expert']:
                score += 10
            
            if volatility == 'medium':
                score += 10
        
        # Cap score at 100
        score = min(100, max(0, score))
        
        return round(score, 1)
    
    def _generate_reasoning(
        self,
        strategy: StrategyType,
        market: Dict,
        profile: Dict,
        score: float
    ) -> str:
        """Generate human-readable reasoning"""
        
        reasons = []
        
        volatility = market.get('volatility', 'medium')
        trend = market.get('trend', 'neutral')
        capital = profile.get('capital', 1000)
        experience = profile.get('experience', 'beginner')
        can_monitor = profile.get('can_monitor', False)
        
        # Market condition reasoning
        if strategy == StrategyType.GRID:
            if volatility == 'low' and trend == 'neutral':
                reasons.append("Perfect for current ranging, low-volatility market")
            else:
                reasons.append("Grid works best in sideways markets")
        
        elif strategy == StrategyType.DCA:
            reasons.append("Safe, passive strategy suitable for all market conditions")
            if not can_monitor:
                reasons.append("Set-and-forget approach ideal for busy schedules")
        
        elif strategy == StrategyType.TURTLE:
            if trend in ['bullish', 'bearish']:
                reasons.append(f"Strong {trend} trend detected - ideal for trend following")
            else:
                reasons.append("Waiting for clear trend to emerge")
        
        elif strategy == StrategyType.AGGRESSIVE_SCALPER:
            if volatility == 'high':
                reasons.append("High volatility provides scalping opportunities")
            if not can_monitor:
                reasons.append("⚠️ Requires active monitoring - not suitable for passive traders")
        
        elif strategy == StrategyType.MEAN_REVERSION:
            if trend == 'neutral':
                reasons.append("Market consolidation ideal for mean reversion trades")
        
        elif strategy == StrategyType.TREND_MASTER:
            if trend in ['bullish', 'bearish']:
                reasons.append(f"Capitalize on current {trend} momentum")
        
        # Capital reasoning
        if capital < 1000 and strategy in [StrategyType.PRICE_ARBITRAGE, StrategyType.LIQUIDITY]:
            reasons.append(f"⚠️ Recommended capital: $2000+, you have: ${capital}")
        
        # Experience reasoning
        if experience == 'beginner' and strategy in [StrategyType.AGGRESSIVE_SCALPER, StrategyType.PRICE_ARBITRAGE]:
            reasons.append("⚠️ Advanced strategy - consider simpler options first")
        
        # Score interpretation
        if score >= 80:
            reasons.insert(0, "🌟 Excellent match for current conditions!")
        elif score >= 60:
            reasons.insert(0, "✅ Good strategy for your profile")
        elif score >= 40:
            reasons.insert(0, "⚠️ Moderate fit - consider alternatives")
        else:
            reasons.insert(0, "❌ Not recommended for current conditions")
        
        return " | ".join(reasons)


# Global instance
selector = StrategyAutoSelector()
