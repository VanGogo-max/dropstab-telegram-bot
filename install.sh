#!/bin/bash

###############################################################################
# CryptoTradeBot Pro - Automatic VPS Installation Script
# Compatible with: Ubuntu 20.04/22.04, Debian 11/12
# Tested on: Vultr, Hostinger, Contabo, DigitalOcean, Kamatera
###############################################################################

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored messages
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }

# Banner
echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║         CryptoTradeBot Pro - Auto Installer              ║
║                   Version 1.0.0                           ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

print_info "Starting installation process..."
echo ""

###############################################################################
# STEP 1: System Update
###############################################################################
print_info "Step 1/10: Updating system packages..."
apt update -qq
apt upgrade -y -qq
print_success "System updated"
echo ""

###############################################################################
# STEP 2: Install Core Dependencies
###############################################################################
print_info "Step 2/10: Installing core dependencies..."
apt install -y -qq \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    curl \
    wget \
    gnupg \
    lsb-release \
    git \
    nano \
    ufw \
    htop

print_success "Core dependencies installed"
echo ""

###############################################################################
# STEP 3: Install Python 3.11
###############################################################################
print_info "Step 3/10: Installing Python 3.11..."
add-apt-repository ppa:deadsnakes/ppa -y
apt update -qq
apt install -y -qq python3.11 python3.11-venv python3-pip python3.11-dev

# Set Python 3.11 as default
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

print_success "Python 3.11 installed"
python3 --version
echo ""

###############################################################################
# STEP 4: Install PostgreSQL
###############################################################################
print_info "Step 4/10: Installing PostgreSQL 15..."
sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
apt update -qq
apt install -y -qq postgresql-15 postgresql-contrib-15

systemctl start postgresql
systemctl enable postgresql

print_success "PostgreSQL 15 installed"
echo ""

###############################################################################
# STEP 5: Install Redis
###############################################################################
print_info "Step 5/10: Installing Redis..."
apt install -y -qq redis-server

# Configure Redis
sed -i 's/supervised no/supervised systemd/' /etc/redis/redis.conf

systemctl restart redis
systemctl enable redis

print_success "Redis installed and configured"
echo ""

###############################################################################
# STEP 6: Install Nginx
###############################################################################
print_info "Step 6/10: Installing Nginx..."
apt install -y -qq nginx

systemctl start nginx
systemctl enable nginx

print_success "Nginx installed"
echo ""

###############################################################################
# STEP 7: Configure Firewall
###############################################################################
print_info "Step 7/10: Configuring firewall..."
ufw --force enable
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw allow 8000/tcp  # FastAPI (temporary)

print_success "Firewall configured"
echo ""

###############################################################################
# STEP 8: Clone Repository
###############################################################################
print_info "Step 8/10: Setting up application..."

# Ask for GitHub repo URL
echo ""
read -p "Enter your GitHub repository URL (or press Enter to skip): " REPO_URL

if [ -z "$REPO_URL" ]; then
    print_warning "Skipping GitHub clone. You'll need to upload files manually."
    mkdir -p /home/cryptobot
else
    print_info "Cloning repository..."
    cd /home
    git clone "$REPO_URL" cryptobot
    print_success "Repository cloned"
fi

cd /home/cryptobot

# Create virtual environment
print_info "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
if [ -f "requirements.txt" ]; then
    print_info "Installing Python packages..."
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    print_success "Python packages installed"
else
    print_warning "requirements.txt not found. Install packages manually later."
fi

echo ""

###############################################################################
# STEP 9: Database Setup
###############################################################################
print_info "Step 9/10: Setting up database..."

# Generate random password
DB_PASSWORD=$(openssl rand -base64 24 | tr -d "=+/" | cut -c1-20)

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE cryptobot;
CREATE USER cryptobot WITH PASSWORD '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE cryptobot TO cryptobot;
\q
EOF

print_success "Database created"
print_info "Database: cryptobot"
print_info "Username: cryptobot"
print_info "Password: $DB_PASSWORD"
echo ""

# Save credentials to file
cat > /home/cryptobot/db_credentials.txt << EOF
Database Credentials:
---------------------
Database: cryptobot
Username: cryptobot
Password: $DB_PASSWORD
Connection String: postgresql://cryptobot:$DB_PASSWORD@localhost:5432/cryptobot

IMPORTANT: Save these credentials! Delete this file after copying them.
EOF

print_warning "Database credentials saved to: /home/cryptobot/db_credentials.txt"
echo ""

###############################################################################
# STEP 10: Create Systemd Service
###############################################################################
print_info "Step 10/10: Creating systemd service..."

cat > /etc/systemd/system/cryptobot.service << EOF
[Unit]
Description=CryptoTradeBot Pro Trading Platform
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=root
WorkingDirectory=/home/cryptobot
Environment="PATH=/home/cryptobot/venv/bin"
ExecStart=/home/cryptobot/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable cryptobot

print_success "Systemd service created"
echo ""

###############################################################################
# Configure Nginx Reverse Proxy
###############################################################################
print_info "Configuring Nginx reverse proxy..."

SERVER_IP=$(curl -s ifconfig.me)

cat > /etc/nginx/sites-available/cryptobot << EOF
server {
    listen 80;
    server_name $SERVER_IP;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

ln -sf /etc/nginx/sites-available/cryptobot /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

nginx -t
systemctl restart nginx

print_success "Nginx configured"
echo ""

###############################################################################
# Create .env template
###############################################################################
print_info "Creating .env template..."

cat > /home/cryptobot/.env.template << EOF
# ==================== DATABASE ====================
DATABASE_URL=postgresql://cryptobot:$DB_PASSWORD@localhost:5432/cryptobot

# ==================== SECURITY ====================
JWT_SECRET=$(openssl rand -base64 32)
JWT_EXPIRATION=86400

# ==================== EXCHANGES ====================
KCEX_API_KEY=your_kcex_api_key_here
KCEX_API_SECRET=your_kcex_secret_here
KCEX_TESTNET=true

HYPERLIQUID_WALLET=your_wallet_address
HYPERLIQUID_PRIVATE_KEY=your_private_key

# ==================== PAYMENT ====================
USDT_WALLET_ADDRESS=your_usdt_wallet_address
POLYGON_RPC_URL=https://polygon-rpc.com

SUBSCRIPTION_PRICE=10
REFERRAL_DISCOUNT=1.00
FREE_REFERRALS_NEEDED=10

# ==================== TELEGRAM ====================
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_ADMIN_ID=your_telegram_user_id

# ==================== ENVIRONMENT ====================
ENVIRONMENT=production
DEBUG=false
GLOBAL_TESTNET=true
LOG_LEVEL=INFO

# ==================== REDIS ====================
REDIS_URL=redis://localhost:6379
EOF

print_success ".env template created at /home/cryptobot/.env.template"
echo ""

###############################################################################
# Installation Complete
###############################################################################
echo ""
echo -e "${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║            Installation Complete! 🎉                      ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

print_success "CryptoTradeBot Pro installed successfully!"
echo ""
print_info "Next Steps:"
echo ""
echo "1. Edit configuration file:"
echo "   nano /home/cryptobot/.env.template"
echo "   → Fill in your API keys"
echo "   → Save as .env (remove .template)"
echo ""
echo "2. Start the application:"
echo "   systemctl start cryptobot"
echo ""
echo "3. Check status:"
echo "   systemctl status cryptobot"
echo ""
echo "4. View logs:"
echo "   journalctl -u cryptobot -f"
echo ""
echo "5. Access application:"
echo "   http://$SERVER_IP"
echo "   API Docs: http://$SERVER_IP/docs"
echo ""
print_warning "Important files to review:"
echo "   • Database credentials: /home/cryptobot/db_credentials.txt"
echo "   • Environment config: /home/cryptobot/.env.template"
echo ""
print_info "Useful commands:"
echo "   • Start bot:   systemctl start cryptobot"
echo "   • Stop bot:    systemctl stop cryptobot"
echo "   • Restart bot: systemctl restart cryptobot"
echo "   • View logs:   journalctl -u cryptobot -f"
echo "   • Edit config: nano /home/cryptobot/.env"
echo ""
print_success "Installation script completed!"
echo ""
