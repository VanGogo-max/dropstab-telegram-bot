# Файл: scraper.py
# Копирай това съдържание в GitHub

# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import sys

class DropsTabScraper:
    BASE_URL = "https://dropstab.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_vwap_data(self):
        """Scrape VWAP Radar data"""
        try:
            url = f"{self.BASE_URL}/coins"
            response = self.session.get(url, timeout=15)
            
            if response.status_code != 200:
                print(f"❌ HTTP Error: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.content, 'lxml')
            coins = []
            
            # Try multiple selectors to find coin data
            rows = (soup.select('tr.coin-row') or 
                   soup.select('div.coin-item') or
                   soup.select('tr[data-coin]'))
            
            if not rows:
                print("❌ No coin rows found. DropsTab HTML may have changed.")
                return None
            
            for row in rows[:20]:  # Top 20 coins
                try:
                    coin = {
                        'name': self._extract_text(row, ['.coin-name', '.name', 'a.coin-link']),
                        'symbol': self._extract_text(row, ['.symbol', '.ticker', '.coin-symbol']),
                        'price': self._extract_number(row, ['.price', '.current-price']),
                        'vwap': self._extract_number(row, ['.vwap-score', '.vwap']),
                        'bullish': self._extract_number(row, ['.bullish-trend', '.trend']),
                        'sector': self._extract_text(row, ['.sector', '.category'])
                    }
                    
                    # Only add if we have essential data
                    if coin['name'] and coin['symbol'] and coin['vwap'] != 0:
                        coins.append(coin)
                except Exception:
                    continue
            
            if not coins:
                print("❌ No valid coin data extracted.")
                return None
                
            print(f"✅ Successfully scraped {len(coins)} coins")
            return coins
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            return None
        except Exception as e:
            print(f"❌ Scraping error: {e}")
            return None
    
    def get_market_sentiment(self):
        """Scrape market sentiment data"""
        try:
            url = f"{self.BASE_URL}/"
            response = self.session.get(url, timeout=15)
            
            if response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.content, 'lxml')
            
            sentiment = {
                'btc_price': self._extract_number(soup, ['.btc-price', '#btc-price', '.bitcoin-price']),
                'btc_change': self._extract_number(soup, ['.btc-change', '.change-24h']),
                'fear_greed': self._extract_number(soup, ['.fear-greed', '#fear-index']),
                'dominance': self._extract_number(soup, ['.btc-dominance', '.dominance']),
                'market_cap': self._extract_number(soup, ['.market-cap', '.total-cap'])
            }
            
            # Check if we got any real data
            if all(v == 0 for v in sentiment.values()):
                print("⚠️ Market sentiment data not found")
                return None
                
            return sentiment
            
        except Exception as e:
            print(f"⚠️ Could not fetch market sentiment: {e}")
            return None
    
    def _extract_text(self, element, selectors):
        """Try multiple selectors to extract text"""
        for selector in selectors:
            try:
                found = element.select_one(selector)
                if found:
                    text = found.get_text(strip=True)
                    if text:
                        return text
            except:
                continue
        return ""
    
    def _extract_number(self, element, selectors):
        """Extract number from element"""
        text = self._extract_text(element, selectors)
        try:
            # Remove common symbols
            cleaned = text.replace('$', '').replace(',', '').replace('%', '')
            cleaned = cleaned.replace('T', '').replace('B', '').replace('M', '').strip()
            
            if cleaned and cleaned != '-':
                return float(cleaned)
        except:
            pass
        return 0
