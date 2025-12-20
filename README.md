# 🤖 CryptoTradeBot Pro

**Automated Crypto Trading Platform**  
7 Professional Trading Bots | Spot & Futures | $10/month

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-teal.svg)](https://fastapi.tiangolo.com)

---

## 🎯 Overview

CryptoTradeBot Pro is an all-in-one automated trading platform featuring 7 professional trading bots for both spot and futures markets. Built for traders who want powerful automation without the complexity.

### 💰 Pricing
- **$10/month** - All features included
- **$1 off per referral** - Unlimited discounts
- **FREE after 10 referrals** 🎉

---

## ✨ Features

### 🤖 7 Trading Bots

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
   
6. **Futures Bot** - Turtle Trading
   - Trend following with pyramiding
   - Best for: Futures on Hyperliquid
   
7. **Arbitrage Bot** - Cross-Exchange
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
git clone https://github.com/yourusername/cryptotradepro.git
cd cryptotradepro

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
│  ├── Bot Manager (7 bots)           │
│  ├── Risk Manager                   │
│  ├── Payment Service (USDT/Polygon) │
│  ├── Referral Service                │
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

**Built with ❤️ by the CryptoTradeBot Pro Team**
