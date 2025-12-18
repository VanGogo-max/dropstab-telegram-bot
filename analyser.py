# Файл: analyzer.py
# Копирай това съдържание в GitHub

# -*- coding: utf-8 -*-

class CryptoAnalyzer:
    """Analyze crypto data based on DropsTab methodology"""
    
    @staticmethod
    def filter_opportunities(coins):
        """Filter coins based on VWAP, Bullish Trend criteria"""
        if not coins:
            return []
            
        opportunities = []
        
        for coin in coins:
            vwap = coin.get('vwap', 0)
            bullish = coin.get('bullish', 0)
            
            # Criteria from algorithm:
            # VWAP: -85 to -100 (oversold)
            # Bullish Trend: 20-50 (starting momentum)
            
            if -100 <= vwap <= -85 and 20 <= bullish <= 50:
                # Calculate score (higher = better opportunity)
                coin['score'] = abs(vwap) + bullish
                opportunities.append(coin)
        
        # Sort by score descending
        opportunities.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return opportunities[:5]  # Top 5 opportunities
    
    @staticmethod
    def categorize_signals(coins):
        """Categorize coins by signal type"""
        if not coins:
            return {'oversold': []}
            
        signals = {
            'oversold': []
        }
        
        for coin in coins:
            vwap = coin.get('vwap', 0)
            
            # Strong oversold (-90 or lower)
            if vwap <= -90:
                signals['oversold'].append(coin)
        
        return signals
    
    @staticmethod
    def assess_market_phase(sentiment):
        """Determine if market is bullish, bearish, or neutral"""
        if not sentiment:
            return 'unknown', '⚪'
            
        btc_change = sentiment.get('btc_change', 0)
        fear_greed = sentiment.get('fear_greed', 50)
        
        if btc_change > 2 and fear_greed > 60:
            return 'bullish', '🟢'
        elif btc_change < -2 and fear_greed < 40:
            return 'bearish', '🔴'
        else:
            return 'neutral', '🟡'
