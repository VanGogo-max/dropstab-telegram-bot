# 🚀 Complete Deployment Guide

## Table of Contents
1. [Server Purchase & Setup](#server-purchase--setup)
2. [Domain & SSL Configuration](#domain--ssl)
3. [Database Setup](#database-setup)
4. [Application Deployment](#application-deployment)
5. [Telegram Bot Setup](#telegram-bot-setup)
6. [Monitoring & Maintenance](#monitoring--maintenance)

---

## 1. Server Purchase & Setup

### Option A: DigitalOcean ($12/month)

**Step 1: Create Account**
```
1. Go to digitalocean.com
2. Sign up (get $200 credit with referral)
3. Add payment method
```

**Step 2: Create Droplet**
```
1. Click "Create" → "Droplets"
2. Choose:
   - Ubuntu 22.04 LTS
   - Basic plan: $12/month (2GB RAM, 50GB SSD)
   - Region: closest to your users
   - Add SSH key (recommended)
3. Create Droplet
4. Note the IP address
```

**Step 3: Initial Server Setup**
```bash
# SSH into server
ssh root@your_server_ip

# Update system
apt update && apt upgrade -y

# Create new user (optional but recommended)
adduser cryptobot
usermod -aG sudo cryptobot
su - cryptobot
```

### Option B: Contabo VPS (€6.99/month - Cheaper!)

```
1. Go to contabo.com
2. Choose VPS S SSD (4GB RAM, 300GB SSD)
3. Select Ubuntu 22.04
4. Complete purchase
5. Receive login credentials via email
6. SSH into server (same as above)
```

### Option C: AWS EC2 Free Tier (First year free)

```
1. Sign up at aws.amazon.com
2. Navigate to EC2
3. Launch Instance:
   - Ubuntu 22.04
   - t2.micro (1GB RAM)
   - Configure security groups
4. Download .pem key
5. SSH: ssh -i key.pem ubuntu@ec2-ip
```

---

## 2. Domain & SSL Configuration

### Buy Domain (Optional but Professional)

**Namecheap ($8.88/year):**
```
1. Go to namecheap.com
2. Search for domain
3. Purchase (use promo codes!)
4. Go to Domain List → Manage → Advanced DNS
5. Add A Record:
   Host: @
   Value: your_server_ip
   TTL: Automatic
6. Add A Record:
   Host: www
   Value: your_server_ip
   TTL: Automatic
```

**Cloudflare DNS (Free):**
```
1. Add site to Cloudflare
2. Update nameservers at Namecheap
3. Add DNS records in Cloudflare
4. Enable Proxy (orange cloud) for security
```

### Setup SSL (Free with Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (already setup)
sudo certbot renew --dry-run
```

---

## 3. Database Setup

### Install PostgreSQL

```bash
# Install
sudo apt install postgresql postgresql-contrib -y

# Start service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql

postgres=# CREATE DATABASE cryptobot;
postgres=# CREATE USER cryptobot WITH PASSWORD 'your_strong_password';
postgres=# GRANT ALL PRIVILEGES ON DATABASE cryptobot TO cryptobot;
postgres=# \q

# Test connection
psql -U cryptobot -d cryptobot -h localhost -W
```

### Install Redis

```bash
# Install
sudo apt install redis-server -y

# Configure
sudo nano /etc/redis/redis.conf
# Set: supervised systemd

# Restart
sudo systemctl restart redis
sudo systemctl enable redis

# Test
redis-cli ping
# Should return: PONG
```

---

## 4. Application Deployment

### Method 1: Direct Deployment (Simpler)

```bash
# Install Python and dependencies
sudo apt install python3.11 python3-pip python3-venv nginx -y

# Clone repository (or upload files)
git clone https://github.com/yourrepo/cryptobot.git
# OR upload via SFTP/SCP from Android

cd cryptobot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env
# Fill in all values

# Test run
python main.py
# Press Ctrl+C after confirming it works
```

### Setup Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/cryptobot.service
```

**Content:**
```ini
[Unit]
Description=CryptoBot Pro Trading Platform
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=cryptobot
WorkingDirectory=/home/cryptobot/cryptobot
Environment="PATH=/home/cryptobot/cryptobot/venv/bin"
ExecStart=/home/cryptobot/cryptobot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable cryptobot
sudo systemctl start cryptobot
sudo systemctl status cryptobot

# View logs
sudo journalctl -u cryptobot -f
```

### Method 2: Docker Deployment (Recommended)

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose -y

# Upload project files
cd /home/cryptobot
# Upload cryptobot folder

# Configure
cd cryptobot
cp .env.example .env
nano .env

# Build and run
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f

# Stop
docker-compose down
```

### Setup Nginx Reverse Proxy

```bash
# Install Nginx
sudo apt install nginx -y

# Create config
sudo nano /etc/nginx/sites-available/cryptobot
```

**Content:**
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/cryptobot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Enable firewall
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

---

## 5. Telegram Bot Setup

### Create Telegram Bot

```
1. Open Telegram
2. Search for @BotFather
3. Send /newbot
4. Choose name: CryptoTradeBot Pro
5. Choose username: YourCryptoBot
6. Save the token
```

### Get Your Telegram ID

```
1. Search for @userinfobot
2. Start conversation
3. Save your user ID
```

### Configure Bot

```bash
# Add to .env
nano .env

TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
TELEGRAM_ADMIN_ID=your_user_id
```

### Start Bot Service

```bash
# Create telegram bot service
sudo nano /etc/systemd/system/telegram-bot.service
```

**Content:**
```ini
[Unit]
Description=CryptoBot Telegram Bot
After=network.target

[Service]
Type=simple
User=cryptobot
WorkingDirectory=/home/cryptobot/cryptobot
Environment="PATH=/home/cryptobot/cryptobot/venv/bin"
ExecStart=/home/cryptobot/cryptobot/venv/bin/python telegram_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
sudo systemctl status telegram-bot
```

### Test Bot

```
1. Open Telegram
2. Search for @YourCryptoBot
3. Send /start
4. Should receive welcome message
```

---

## 6. Monitoring & Maintenance

### Setup Monitoring

**Install Monitoring Tools:**
```bash
# Install htop
sudo apt install htop -y

# Install monitoring script
sudo apt install sysstat -y
```

### Daily Checks

```bash
# Check services
sudo systemctl status cryptobot
sudo systemctl status telegram-bot
sudo systemctl status postgresql
sudo systemctl status redis

# Check logs
sudo journalctl -u cryptobot -n 50
tail -f /home/cryptobot/cryptobot/cryptobot.log

# Check disk space
df -h

# Check memory
free -m

# Check processes
htop
```

### Backup Strategy

**Database Backup:**
```bash
# Create backup script
nano ~/backup.sh
```

**Content:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/cryptobot/backups"
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U cryptobot cryptobot > $BACKUP_DIR/db_$DATE.sql

# Backup .env
cp /home/cryptobot/cryptobot/.env $BACKUP_DIR/env_$DATE

# Delete old backups (keep 7 days)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete

echo "Backup completed: $DATE"
```

```bash
# Make executable
chmod +x ~/backup.sh

# Setup daily cron
crontab -e
# Add: 0 2 * * * /home/cryptobot/backup.sh
```

### Update Application

```bash
# Pull latest code
cd /home/cryptobot/cryptobot
git pull

# Restart services
sudo systemctl restart cryptobot
sudo systemctl restart telegram-bot

# Check status
sudo systemctl status cryptobot
```

### Security Hardening

```bash
# Change SSH port
sudo nano /etc/ssh/sshd_config
# Change Port 22 to Port 2222

# Disable root login
# Set PermitRootLogin no

# Restart SSH
sudo systemctl restart sshd

# Install fail2ban
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## Quick Troubleshooting

### Application won't start
```bash
# Check logs
sudo journalctl -u cryptobot -n 100

# Check Python errors
python main.py
```

### Database connection failed
```bash
# Check PostgreSQL
sudo systemctl status postgresql

# Test connection
psql -U cryptobot -d cryptobot -h localhost -W
```

### Telegram bot not responding
```bash
# Check service
sudo systemctl status telegram-bot

# Check logs
sudo journalctl -u telegram-bot -n 50

# Restart
sudo systemctl restart telegram-bot
```

---

## Cost Summary

### Minimum Setup (€10/month):
- Contabo VPS: €6.99/month
- Domain: €8.88/year (€0.74/month)
- SSL: Free (Let's Encrypt)
- Total: ~€8/month

### Recommended Setup ($20/month):
- DigitalOcean Droplet: $12/month
- Domain: $8.88/year
- Cloudflare: Free
- Total: ~$13/month

### Professional Setup ($50/month):
- AWS/GCP: $30-40/month
- Domain + Email: $10/month
- Monitoring tools: Free
- Total: ~$40-50/month

---

## Support Checklist

✅ Server purchased and accessed
✅ Domain configured (optional)
✅ SSL installed
✅ PostgreSQL running
✅ Redis running
✅ Application deployed
✅ Nginx configured
✅ Telegram bot running
✅ Backups automated
✅ Monitoring setup

**You're live! 🎉**

Access your bot:
- Web: https://yourdomain.com
- Telegram: @YourCryptoBot
- API: https://yourdomain.com/docs

---

Need help? Check logs first, then contact support.
