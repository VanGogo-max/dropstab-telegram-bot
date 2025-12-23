# 🤖 CryptoTradeBot Pro

**Automated Crypto Trading Platform**  
10 Professional Trading Bots | Spot & Futures | $10/month

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-teal.svg)](https://fastapi.tiangolo.com)

---

## 🎯 Overview

CryptoTradeBot Pro is an all-in-one automated trading platform featuring **10 professional trading bots** for both spot and futures markets. Built for traders who want powerful automation without the complexity.

### 💰 Pricing
- **$10/month** - All features included
- **$1 off per referral** - Unlimited discounts
- **FREE after 10 referrals** 🎉

---

## ✨ Features

### 🤖 10 Trading Bots

#### **Simple Automation Bots (5)**
1. **DCA Bot** - Dollar Cost Averaging
   - Auto-buy at regular intervals
   - Best for: Long-term accumulation
   
2. **Signal Bot** - Technical Analysis
   - RSI, MACD, Bollinger Bands
   - Best for: Swing trading
   
3. **Portfolio Bot** - Auto Rebalancing
   - Maintain target allocation
   - Best for: Diversification
   
4. **Trailing Stop Bot** - Profit Protection
   - Follow price up, sell on dip
   - Best for: Locking gains
   
5. **Grid Bot** - Grid Trading
   - Buy low, sell high automatically
   - Best for: Ranging markets

#### **Advanced Strategy Bots (3)** 🆕
6. **Aggressive Scalper** - High-Frequency Momentum
   - 5-minute scalping on Hyperliquid
   - Risk: HIGH | Win Rate: 60% | R:R 1:3
   - Best for: Experienced traders

7. **Trend Master** - Smart Trend Following
   - 4h trends with 15m pullback entries
   - Risk: MEDIUM | Win Rate: 70% | R:R 1:2
   - Best for: Swing traders

8. **Mean Reversion Pro** - Bollinger Bands Strategy
   - 1h mean reversion on KCEX
   - Risk: LOW | Win Rate: 65% | R:R 1:1.5
   - Best for: Conservative traders

#### **Professional Bots (2)**
9. **Turtle Futures Bot** - Trend Following
   - Classic Turtle Trading with pyramiding
   - Best for: Futures on Hyperliquid
   
10. **Arbitrage Bot** - Cross-Exchange
    - Profit from price differences
    - Best for: Multi-exchange users

### 🌐 Supported Exchanges

- **Spot Trading:** KCEX
- **Futures Trading:** Hyperliquid (Arbitrum Network)
- **Arbitrage:** KCEX + Binance/OKX

### 🔒 Security & Risk Management

- Conservative risk limits (2% per trade max)
- Stop-loss on all positions
- Emergency circuit breakers
- API keys encrypted
- Testnet mode for practice

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- Docker (optional)

### Installation

```bash
# Clone repository
git clone https://github.com/VanGogo-max/dropstab-telegram-bot.git
cd dropstab-telegram-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Run database migrations
python -m alembic upgrade head

# Start application
python main.py
```

### Docker Setup

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## 📖 Documentation

- **[Quick Start Guide](QUICK_START.md)** - Get up and running in 5 minutes
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment
- **[Pricing Details](PRICING.md)** - Subscription & referral info
- **[Bot Strategies](BOT_STRATEGIES.md)** - Complete guide to all 10 bots
- **[API Documentation](docs/API.md)** - REST API reference

---

## 🎁 Referral Program

### Earn $1 Off Per Referral

1. Get your unique referral code
2. Share with friends
3. They save $1 on first month ($9)
4. You save $1 every month they stay subscribed
5. **Get 10 referrals = FREE forever!**

**Example:**
```
5 referrals = $5/month (save $60/year)
10 referrals = FREE (save $120/year)
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│         Frontend (React)            │
│  Web App + Mobile App + Dashboards  │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      FastAPI Backend (Python)       │
│  ├── Bot Manager (10 bots)          │
│  ├── Risk Manager                   │
│  ├── Payment Service (USDT/Polygon) │
│  ├── Referral Service               │
│  └── Email/Telegram Notifications   │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Exchanges                   │
│  ├── KCEX (Spot)                    │
│  ├── Hyperliquid (Futures/Arbitrum) │
│  └── Binance/OKX (Arbitrage)        │
└─────────────────────────────────────┘
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend

# Test specific bot
pytest tests/test_dca_bot.py
```

---

## 📊 Tech Stack

**Backend:**
- Python 3.11
- FastAPI (REST API)
- PostgreSQL (Database)
- Redis (Caching)
- SQLAlchemy (ORM)
- ccxt (Exchange integration)

**Frontend:**
- React + TypeScript
- React Native (Mobile)
- Recharts (Analytics)
- TailwindCSS (Styling)

**Infrastructure:**
- Docker + docker-compose
- Nginx (Reverse proxy)
- Let's Encrypt (SSL)

---

## 📋 Bot Comparison

| Bot | Risk | Exchange | Win Rate | Duration | Best For |
|-----|------|----------|----------|----------|----------|
| DCA | 🟢 Low | KCEX | N/A | Continuous | Accumulation |
| Signal | 🟡 Medium | KCEX | 65% | Hours-Days | Swing Trading |
| Portfolio | 🟢 Low | KCEX | N/A | Weekly | Diversification |
| Trailing | 🟢 Low | KCEX | N/A | Active | Profit Lock |
| Grid | 🟡 Medium | KCEX | 70% | Continuous | Ranging |
| Aggressive Scalper | 🔴 High | Hyperliquid | 60% | Minutes | Scalping |
| Trend Master | 🟡 Medium | KCEX | 70% | 1-7 Days | Trends |
| Mean Reversion | 🟢 Low | KCEX | 65% | 2-5 Days | Sideways |
| Turtle Futures | 🔴 High | Hyperliquid | 60% | Weeks | Trends |
| Arbitrage | 🟢 Low | Multi | 80% | Seconds | Any Market |

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

## 📜 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🆘 Support

**Email:** support@cryptotradepro.com  
**Telegram:** @cryptotradepro_bot  
**Discord:** discord.gg/cryptotradepro

---

## ⚠️ Disclaimer

Trading cryptocurrencies carries risk. This software is provided "as is" without warranty. Always do your own research and never invest more than you can afford to lose.

---

## 🌟 Star Us!

If you find this project useful, please consider giving it a ⭐ on GitHub!

---

## 📈 Recent Updates

### v2.0.0 (December 2024)
- ✨ Added 3 new advanced strategy bots
- 🔥 Aggressive Scalper for high-frequency trading
- 📈 Trend Master with smart pullback entries
- 🎯 Mean Reversion Pro for ranging markets
- 💰 Reduced pricing to $10/month
- 🎁 New referral system: $1/referral, FREE after 10
- 📚 Complete bot strategy documentation
- 🔧 KCEX and Hyperliquid integration

### v1.0.0 (November 2024)
- 🎉 Initial release with 7 bots
- ⚡ Spot and futures trading
- 💳 USDT payment on Polygon
- 📊 Admin and analytics dashboards

---

**Built with ❤️ by the CryptoTradeBot Pro Team**

*Last updated: December 2024*
