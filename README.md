# 🤖 DropsTab Telegram Bot

Multi-language crypto analysis bot with Spot Grid & Futures trading integration.

---

## 🎯 Features

- 🌍 **9 Languages**: EN, BG, RU, ES, TR, DE, AR, ZH, HI
- 📊 **Smart Analysis**: VWAP, Bullish Trend, Market Sentiment
- 🔗 **Trading Integration**: One-click connection to Spot & Futures bots
- 💎 **Flexible Plans**: Free, Premium ($5), Pro ($15)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))

### Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/dropstab-telegram-bot.git
cd dropstab-telegram-bot

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your credentials

# Run bot
python bot.py
```

---

## ⚙️ Configuration

Create `.env` file:

```env
BOT_TOKEN=your_bot_token_here
DATABASE_URL=postgresql://user:password@localhost/dropstab_bot
SPOT_BOT_USERNAME=YourSpotGridBot
FUTURES_BOT_USERNAME=YourAureaBot
ADMIN_USER_ID=your_telegram_user_id
```

---

## 📊 Pricing Tiers

### 🆓 FREE
- 1 analysis per day
- 1 language
- Basic signals

### 💎 PREMIUM ($5/month)
- Unlimited analyses
- 3 languages
- Auto daily analysis at 6 AM
- Quick trade buttons

### 🚀 PRO ($15/month)
- All Premium features
- All 9 languages
- Custom alerts
- Auto-trade webhooks
- 30-day history

---

## 🛠️ Deployment

### VPS Deployment (Recommended)

```bash
# On your VPS
git clone https://github.com/YOUR_USERNAME/dropstab-telegram-bot.git
cd dropstab-telegram-bot

# Install dependencies
pip3 install -r requirements.txt

# Setup PostgreSQL
sudo apt install postgresql
sudo -u postgres createdb dropstab_bot

# Configure environment
nano .env  # Add your credentials

# Run with systemd (persistent)
sudo nano /etc/systemd/system/dropstab-bot.service
```

**systemd service file:**
```ini
[Unit]
Description=DropsTab Telegram Bot
After=network.target

[Service]
Type=simple
User=YOUR_USER
WorkingDirectory=/path/to/dropstab-telegram-bot
ExecStart=/usr/bin/python3 /path/to/dropstab-telegram-bot/bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable dropstab-bot
sudo systemctl start dropstab-bot
sudo systemctl status dropstab-bot
```

---

## 🔗 Integrated Bots

- **Spot Grid Bot**: [@YourSpotGridBot](https://t.me/YourSpotGridBot)
- **Futures Bot**: [@YourAureaBot](https://t.me/YourAureaBot)

---

## 📝 Commands

```
/start - Start the bot
/analyze - Generate crypto analysis
/upgrade - View premium plans
/status - Check subscription
/help - Show all commands
```

---

## 🤝 Support

- Telegram: [@YourUsername](https://t.me/YourUsername)
- Issues: [GitHub Issues](https://github.com/YOUR_USERNAME/dropstab-telegram-bot/issues)

---

## 📜 License

No License - All rights reserved

---

Made with ❤️ for the crypto community
