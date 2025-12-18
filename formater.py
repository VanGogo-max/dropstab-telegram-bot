# Файл: formatter.py
# Копирай това съдържание в GitHub

# -*- coding: utf-8 -*-
from datetime import datetime
from translations import get_translation

class TelegramFormatter:
    """Format analysis data for Telegram posts"""
    
    @staticmethod
    def format_analysis(sentiment, opportunities, lang='en'):
        """Generate complete Telegram post"""
        t = get_translation(lang)
        date = datetime.now().strftime('%Y-%m-%d')
        
        # Header
        post = f"{t['title']} | {date}\n\n"
        
        # Market Sentiment Section
        post += f"{t['market_sentiment']}\n"
        post += "━━━━━━━━━━━━━━━━━━\n"
        
        if sentiment:
            btc_price = sentiment.get('btc_price', 0)
            btc_change = sentiment.get('btc_change', 0)
            btc_emoji = '🟢' if btc_change > 0 else '🔴'
            
            if btc_price > 0:
                post += f"Bitcoin: ${btc_price:,.0f} | {btc_emoji} {btc_change:+.1f}%\n"
            
            fg = sentiment.get('fear_greed', 0)
            if fg > 0:
                fg_text = 'Greed' if fg > 50 else 'Fear'
                post += f"{t['fear_greed']}: {fg} | {fg_text}\n"
            
            dom = sentiment.get('dominance', 0)
            if dom > 0:
                post += f"{t['dominance']}: {dom:.1f}%\n"
            
            mcap = sentiment.get('market_cap', 0)
            if mcap > 0:
                post += f"{t['market_cap']}: ${mcap:.2f}T\n"
        else:
            post += "Market data unavailable\n"
        
        post += "\n━━━━━━━━━━━━━━━━━━\n\n"
        
        # Top Opportunities Section
        post += f"{t['top_opportunities']}\n\n"
        
        if opportunities:
            for i, coin in enumerate(opportunities[:3], 1):
                name = coin.get('name', 'Unknown')
                symbol = coin.get('symbol', '')
                price = coin.get('price', 0)
                vwap = coin.get('vwap', 0)
                bullish = coin.get('bullish', 0)
                sector = coin.get('sector', '')
                
                post += f"💎 #{i}: {name} ({symbol})\n"
                post += f"├─ {t['price']}: ${price:.2f}"
                
                if sector:
                    post += f" | {t['sector']}: {sector}\n"
                else:
                    post += "\n"
                
                post += f"├─ {t['vwap_score']}: {vwap:.0f} ✅\n"
                post += f"├─ {t['bullish_trend']}: {bullish:.0f}/100 ✅\n"
                post += f"└─ {t['investors']}: Tier 1\n\n"
        else:
            post += "No opportunities found matching criteria.\n\n"
        
        post += "━━━━━━━━━━━━━━━━━━\n\n"
        
        # Quick Signals Section
        post += f"{t['quick_signals']}\n\n"
        
        if opportunities:
            oversold = [c for c in opportunities if c.get('vwap', 0) <= -90]
            if oversold:
                symbols = ' | '.join([c.get('symbol', '') for c in oversold[:5]])
                post += f"{t['oversold']}:\n• {symbols}\n\n"
        
        post += "━━━━━━━━━━━━━━━━━━\n\n"
        
        # Disclaimer
        post += f"{t['disclaimer']}\n\n"
        post += f"{t['data_source']} | {date}"
        
        return post
