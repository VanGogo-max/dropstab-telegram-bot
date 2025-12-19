# 🚀 CryptoTradeBot Pro

Professional crypto trading platform with 7 autonomous bots, subscription system, and multi-platform support.

## 📋 Features

### Trading Bots
- **DCA Bot** - Dollar Cost Averaging strategy
- **Signal Bot** - Technical analysis signals (RSI, MACD, BB)
- **Portfolio Bot** - Automatic rebalancing
- **Trailing Stop Bot** - Profit protection
- **Arbitrage Bot** - Cross-exchange opportunities
- **Grid Bot** - Grid trading (existing)
- **Futures Bot** - Futures trading (existing)

### Platform Features
- 💳 USDT Polygon payments
- 🎁 Referral system (20% discount per referral, free after 5)
- 🔐 Admin panel with password protection
- 🌍 Web, Mobile & Telegram apps
- 🎨 Hyperliquid-inspired design
- 🔔 Real-time notifications
- 📊 Performance analytics

## 💰 Pricing

**Single Plan: $39/month**
- Full access to all bots
- Unlimited trading pairs
- Priority support

**Referral Discounts:**
- 1 referral = 20% off ($31.20/month)
- 3 referrals = 50% off ($19.50/month)
- 5 referrals = **FREE!**

---

## 🛠️ Installation

### Prerequisites
- Python 3.9+
- PostgreSQL 14+
- Redis 6+
- Node.js 18+ (for frontend)

### 1. Clone Repository
```bash
git clone https://github.com/yourrepo/cryptobot.git
cd cryptobot
```

### 2. Setup Backend
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your values
```

### 3. Setup Database
```bash
# Create PostgreSQL database
createdb cryptobot

# Run migrations
python database.py migrate

# Create admin user
python scripts/create_admin.py
```

### 4. Configure Exchange APIs
Edit `.env` and add your exchange API keys:
```env
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret
```

### 5. Start Backend
```bash
python main.py
```

---

## 🐳 Docker Deployment

### Using Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: cryptobot
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6
    volumes:
      - redis_data:/data

  backend:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      - postgres
      - redis

volumes:
  postgres_data:
  redis_data:
```

```bash
docker-compose up -d
```

---

## ☁️ Server Setup (VPS/Cloud)

### Option 1: DigitalOcean ($12/month)
```bash
# 1. Create Droplet (Ubuntu 22.04, 2GB RAM)
# 2. SSH into server
ssh root@your-server-ip

# 3. Install dependencies
apt update
apt install -y python3.9 python3-pip postgresql redis-server nginx

# 4. Clone and setup
git clone your-repo
cd cryptobot
pip3 install -r requirements.txt

# 5. Setup systemd service
nano /etc/systemd/system/cryptobot.service
```

**cryptobot.service:**
```ini
[Unit]
Description=CryptoBot Pro
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/cryptobot
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
systemctl enable cryptobot
systemctl start cryptobot
systemctl status cryptobot
```

### Option 2: AWS EC2
```bash
# 1. Launch t3.small instance (Ubuntu 22.04)
# 2. Configure security groups (ports 22, 80, 443, 8000)
# 3. Same setup as above
```

### Option 3: Google Cloud Run (Serverless)
```bash
# 1. Install gcloud CLI
# 2. Build container
docker build -t gcr.io/your-project/cryptobot .

# 3. Push to registry
docker push gcr.io/your-project/cryptobot

# 4. Deploy
gcloud run deploy cryptobot \
  --image gcr.io/your-project/cryptobot \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## 🤖 Telegram Bot Setup

### 1. Create Bot
```bash
# Talk to @BotFather on Telegram
/newbot
# Follow prompts, save token
```

### 2. Get Your User ID
```bash
# Talk to @userinfobot
# Save your user_id as TELEGRAM_ADMIN_ID
```

### 3. Configure
```env
# .env
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_ADMIN_ID=your_user_id
```

### 4. Start Bot
```bash
python telegram_bot.py
```

### Commands
```
/start - Start bot
/balance - Check balance
/bots - Manage bots
/start_dca - Start DCA bot
/start_signal - Start Signal bot
/portfolio - View portfolio
/referral - Get referral link
/help - Help
```

---

## 🔧 Configuration

### Risk Settings (config.py)
```python
RISK_CONFIG = {
    'max_position_size': 0.10,  # 10% per trade
    'max_daily_loss': 0.05,     # 5% daily limit
    'max_drawdown': 0.10,       # 10% max loss
    'stop_loss_percent': 0.03   # 3% stop loss
}
```

### Bot Settings
Each bot has customizable settings in `config.py`. Edit as needed.

---

## 📱 Frontend Deployment

### Web App (React)
```bash
cd frontend/web
npm install
npm run build

# Deploy to Vercel/Netlify
vercel deploy
# or
netlify deploy
```

### Mobile App (React Native)
```bash
cd frontend/mobile
npm install

# iOS
cd ios && pod install
npx react-native run-ios

# Android
npx react-native run-android
```

---

## 🔒 Security Best Practices

1. **Change default passwords**
```bash
# .env
ADMIN_PASSWORD=use-strong-password-here
SECRET_KEY=generate-random-string
```

2. **Enable SSL/HTTPS**
```bash
# Install certbot
sudo certbot --nginx -d yourdomain.com
```

3. **Firewall**
```bash
# Allow only necessary ports
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

4. **API Key Permissions**
- Enable only necessary permissions
- Disable withdrawals on exchange
- Use IP whitelist if available

---

## 📊 Monitoring

### Logs
```bash
# View logs
tail -f cryptobot.log

# systemd logs
journalctl -u cryptobot -f
```

### Health Check
```bash
curl http://localhost:8000/health
```

---

## 🐛 Troubleshooting

### Bot not starting
```bash
# Check logs
tail -f cryptobot.log

# Check database connection
psql -U user -d cryptobot -c "SELECT 1;"

# Restart services
systemctl restart cryptobot
```

### Payment not verifying
- Check Polygon RPC endpoint
- Verify payment address
- Check transaction on PolygonScan

### Exchange API errors
- Verify API keys
- Check permissions
- Try testnet first

---

## 📈 Performance Tips

1. **Use Redis caching** for price data
2. **Enable testnet** for initial testing
3. **Start with small positions**
4. **Monitor risk metrics** daily
5. **Use conservative settings** initially

---

## 🤝 Support

- Documentation: [docs.yourapp.com](https://docs.yourapp.com)
- Telegram: [@yourbot_support](https://t.me/yourbot_support)
- Email: support@yourapp.com

---

## 📄 License

Proprietary - All rights reserved

---

## 🎯 Roadmap

- [ ] Mobile push notifications
- [ ] Copy trading feature
- [ ] Advanced analytics dashboard
- [ ] Multi-user management
- [ ] API for third-party integrations

---

**⚠️ Disclaimer:** Crypto trading involves risk. Past performance doesn't guarantee future results. Trade responsibly.
