# ⚡ Quick Start Guide

Пусни платформата за 15 минути!

## 📋 Prerequisites (One-time setup)

```bash
# Install Python 3.11
sudo apt install python3.11 python3-pip -y

# Install PostgreSQL
sudo apt install postgresql -y

# Install Redis
sudo apt install redis-server -y

# Install Node.js (for frontend)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y
```

---

## 🚀 Quick Setup (5 минути)

### 1. Clone/Upload Project
```bash
# From Git
git clone https://github.com/yourrepo/cryptobot.git
cd cryptobot

# OR upload files via SFTP from Android
```

### 2. Backend Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
nano .env
# Fill in required values (API keys, passwords)
```

### 3. Database Setup
```bash
# Create database
sudo -u postgres psql
postgres=# CREATE DATABASE cryptobot;
postgres=# CREATE USER cryptobot WITH PASSWORD 'your_password';
postgres=# GRANT ALL PRIVILEGES ON DATABASE cryptobot TO cryptobot;
postgres=# \q

# Initialize tables
python database.py
```

### 4. Start Backend
```bash
# Test run
python main.py

# If working, setup as service (see DEPLOYMENT.md)
# Or run in background:
nohup python main.py > output.log 2>&1 &
```

### 5. Start Telegram Bot
```bash
# In new terminal
source venv/bin/activate
python telegram_bot.py

# Or background:
nohup python telegram_bot.py > telegram.log 2>&1 &
```

---

## 🧪 Test Everything

### Test Backend API
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

### Test Telegram Bot
```
1. Open Telegram
2. Search for your bot
3. Send /start
4. Should receive welcome message
```

### Test Database
```bash
psql -U cryptobot -d cryptobot -c "SELECT 1;"
# Should return: 1
```

---

## 🎨 Frontend Setup (Optional)

```bash
cd frontend
npm install
npm run dev

# Access at http://localhost:5173
```

---

## ⚙️ Configure Bots

### Add Exchange API Keys

```bash
nano .env

# Add your keys:
BINANCE_API_KEY=your_key_here
BINANCE_API_SECRET=your_secret_here
```

### Start Your First Bot

Via Telegram:
```
/start_dca BTC/USDT
```

Via API:
```bash
curl -X POST http://localhost:8000/api/bots/dca/start \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "symbol": "BTC/USDT",
    "interval_hours": 24,
    "amount_per_order": 50
  }'
```

---

## 📊 Monitor Bots

### Check Status
```bash
# Via Telegram
/status

# Via API
curl http://localhost:8000/api/bots/status?user_id=test_user
```

### View Logs
```bash
tail -f cryptobot.log
tail -f telegram.log
```

---

## 🛑 Stop Everything

```bash
# Stop bots (via Telegram)
/stop <bot_id>

# Stop services
pkill -f main.py
pkill -f telegram_bot.py

# Or if using systemd:
sudo systemctl stop cryptobot
sudo systemctl stop telegram-bot
```

---

## 🔥 Production Deployment (Once Working)

```bash
# Follow DEPLOYMENT.md for:
# - Domain setup
# - SSL certificate
# - Nginx reverse proxy
# - Systemd services
# - Automated backups
```

---

## 🆘 Common Issues

### Port already in use
```bash
# Kill process on port 8000
sudo lsof -ti:8000 | xargs kill -9
```

### Database connection failed
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Restart if needed
sudo systemctl restart postgresql
```

### Telegram bot not responding
```bash
# Check token in .env
# Verify bot is running:
ps aux | grep telegram_bot.py

# Check logs:
tail -f telegram.log
```

### Exchange API errors
```bash
# Verify API keys are correct
# Check if testnet is enabled (should be True for testing)
# Check exchange status
```

---

## ✅ Success Checklist

- [ ] Backend running on port 8000
- [ ] Database created and accessible
- [ ] Redis running
- [ ] Telegram bot responding
- [ ] Exchange API keys configured
- [ ] First bot started successfully
- [ ] Logs show no errors

**Готов си! 🎉**

---

## 📚 Next Steps

1. **Test on Testnet** - Always test first!
2. **Configure Risk Settings** - Edit config.py
3. **Setup Monitoring** - Follow DEPLOYMENT.md
4. **Enable Production** - Switch testnet=False when ready
5. **Setup Backups** - Automate database backups

---

## 💡 Pro Tips

### Quick Restart All
```bash
#!/bin/bash
# restart_all.sh
pkill -f main.py
pkill -f telegram_bot.py
sleep 2
source venv/bin/activate
nohup python main.py > output.log 2>&1 &
nohup python telegram_bot.py > telegram.log 2>&1 &
echo "All services restarted!"
```

### Monitor Dashboard
```bash
watch -n 5 'curl -s http://localhost:8000/api/admin/stats?password=your_password | jq'
```

### Backup Quick
```bash
pg_dump -U cryptobot cryptobot > backup_$(date +%Y%m%d).sql
```

---

**Need help?** Check:
- README.md - Full documentation
- DEPLOYMENT.md - Production setup
- Logs - Always check logs first!

**Support:** @yourbot_support on Telegram
