#!/bin/bash
# system_monitor.sh - Real-time System Monitoring & Alerts

# Configuration
APP_DIR="/home/cryptobot/cryptobot"
LOG_FILE="$APP_DIR/cryptobot.log"
TELEGRAM_LOG="$APP_DIR/telegram.log"
ALERT_EMAIL="admin@cryptobot.com"

# Thresholds
CPU_THRESHOLD=80
MEMORY_THRESHOLD=85
DISK_THRESHOLD=90

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ====================================
# SYSTEM CHECKS
# ====================================

check_cpu() {
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    CPU_INT=${CPU_USAGE%.*}
    
    if [ $CPU_INT -gt $CPU_THRESHOLD ]; then
        echo -e "${RED}⚠ CPU Usage: ${CPU_USAGE}% (HIGH)${NC}"
        return 1
    else
        echo -e "${GREEN}✓ CPU Usage: ${CPU_USAGE}%${NC}"
        return 0
    fi
}

check_memory() {
    MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    
    if [ $MEMORY_USAGE -gt $MEMORY_THRESHOLD ]; then
        echo -e "${RED}⚠ Memory Usage: ${MEMORY_USAGE}% (HIGH)${NC}"
        return 1
    else
        echo -e "${GREEN}✓ Memory Usage: ${MEMORY_USAGE}%${NC}"
        return 0
    fi
}

check_disk() {
    DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | cut -d'%' -f1)
    
    if [ $DISK_USAGE -gt $DISK_THRESHOLD ]; then
        echo -e "${RED}⚠ Disk Usage: ${DISK_USAGE}% (HIGH)${NC}"
        return 1
    else
        echo -e "${GREEN}✓ Disk Usage: ${DISK_USAGE}%${NC}"
        return 0
    fi
}

check_services() {
    echo -e "${BLUE}=== Service Status ===${NC}"
    
    # Check main application
    if pgrep -f "main.py" > /dev/null; then
        echo -e "${GREEN}✓ Main Application: Running${NC}"
    else
        echo -e "${RED}✗ Main Application: Not Running${NC}"
    fi
    
    # Check Telegram bot
    if pgrep -f "telegram_bot.py" > /dev/null; then
        echo -e "${GREEN}✓ Telegram Bot: Running${NC}"
    else
        echo -e "${RED}✗ Telegram Bot: Not Running${NC}"
    fi
    
    # Check PostgreSQL
    if systemctl is-active --quiet postgresql; then
        echo -e "${GREEN}✓ PostgreSQL: Running${NC}"
    else
        echo -e "${RED}✗ PostgreSQL: Not Running${NC}"
    fi
    
    # Check Redis
    if systemctl is-active --quiet redis; then
        echo -e "${GREEN}✓ Redis: Running${NC}"
    else
        echo -e "${RED}✗ Redis: Not Running${NC}"
    fi
    
    # Check Nginx (if installed)
    if systemctl is-active --quiet nginx 2>/dev/null; then
        echo -e "${GREEN}✓ Nginx: Running${NC}"
    else
        echo -e "${YELLOW}⚠ Nginx: Not installed or not running${NC}"
    fi
}

check_database() {
    echo -e "${BLUE}=== Database Status ===${NC}"
    
    # Check database connection
    if psql -U cryptobot -d cryptobot -c "SELECT 1" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Database Connection: OK${NC}"
        
        # Get database size
        DB_SIZE=$(psql -U cryptobot -d cryptobot -t -c "SELECT pg_size_pretty(pg_database_size('cryptobot'));" | xargs)
        echo -e "${GREEN}  Database Size: $DB_SIZE${NC}"
        
        # Get table counts
        USER_COUNT=$(psql -U cryptobot -d cryptobot -t -c "SELECT COUNT(*) FROM users;" 2>/dev/null | xargs)
        echo -e "${GREEN}  Total Users: ${USER_COUNT:-0}${NC}"
        
    else
        echo -e "${RED}✗ Database Connection: Failed${NC}"
    fi
}

check_api() {
    echo -e "${BLUE}=== API Health Check ===${NC}"
    
    # Check local API
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✓ API Health: OK (HTTP $HTTP_CODE)${NC}"
        
        # Get API stats
        RESPONSE=$(curl -s http://localhost:8000/health)
        echo -e "${GREEN}  Response: $RESPONSE${NC}"
    else
        echo -e "${RED}✗ API Health: Failed (HTTP $HTTP_CODE)${NC}"
    fi
}

check_logs() {
    echo -e "${BLUE}=== Recent Errors ===${NC}"
    
    # Check for errors in main log
    if [ -f "$LOG_FILE" ]; then
        ERROR_COUNT=$(grep -c "ERROR" "$LOG_FILE" 2>/dev/null || echo 0)
        echo -e "${YELLOW}Main Log Errors (last 24h): $ERROR_COUNT${NC}"
        
        if [ $ERROR_COUNT -gt 0 ]; then
            echo "Last 3 errors:"
            tail -n 100 "$LOG_FILE" | grep "ERROR" | tail -3
        fi
    fi
    
    # Check Telegram bot errors
    if [ -f "$TELEGRAM_LOG" ]; then
        TG_ERROR_COUNT=$(grep -c "ERROR" "$TELEGRAM_LOG" 2>/dev/null || echo 0)
        echo -e "${YELLOW}Telegram Bot Errors: $TG_ERROR_COUNT${NC}"
    fi
}

check_network() {
    echo -e "${BLUE}=== Network Status ===${NC}"
    
    # Check internet connection
    if ping -c 1 8.8.8.8 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Internet Connection: OK${NC}"
    else
        echo -e "${RED}✗ Internet Connection: Failed${NC}"
    fi
    
    # Check open ports
    echo "Open Ports:"
    netstat -tuln | grep LISTEN | grep -E ':(8000|5432|6379|80|443)' | awk '{print "  "$4}'
}

# ====================================
# MONITORING REPORTS
# ====================================

full_status() {
    clear
    echo -e "${GREEN}=========================================${NC}"
    echo -e "${GREEN}   CRYPTOBOT PRO - SYSTEM STATUS${NC}"
    echo -e "${GREEN}=========================================${NC}"
    echo -e "${YELLOW}$(date)${NC}"
    echo ""
    
    check_cpu
    check_memory
    check_disk
    echo ""
    
    check_services
    echo ""
    
    check_database
    echo ""
    
    check_api
    echo ""
    
    check_network
    echo ""
    
    check_logs
    echo ""
    
    echo -e "${GREEN}=========================================${NC}"
}

watch_status() {
    while true; do
        full_status
        echo ""
        echo -e "${YELLOW}Refreshing in 5 seconds... (Ctrl+C to stop)${NC}"
        sleep 5
    done
}

# ====================================
# ALERTS
# ====================================

send_alert() {
    SUBJECT="$1"
    MESSAGE="$2"
    
    echo "Alert: $SUBJECT"
    echo "$MESSAGE"
    
    # Send email (if configured)
    # echo "$MESSAGE" | mail -s "$SUBJECT" $ALERT_EMAIL
    
    # Send to Telegram (if configured)
    # curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
    #   -d chat_id=$ADMIN_CHAT_ID \
    #   -d text="$SUBJECT\n$MESSAGE"
}

check_critical() {
    ISSUES=()
    
    # Check if services are running
    if ! pgrep -f "main.py" > /dev/null; then
        ISSUES+=("Main application is not running")
    fi
    
    if ! pgrep -f "telegram_bot.py" > /dev/null; then
        ISSUES+=("Telegram bot is not running")
    fi
    
    # Check resource usage
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1 | cut -d'.' -f1)
    if [ $CPU_USAGE -gt 90 ]; then
        ISSUES+=("CPU usage critical: ${CPU_USAGE}%")
    fi
    
    MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    if [ $MEMORY_USAGE -gt 90 ]; then
        ISSUES+=("Memory usage critical: ${MEMORY_USAGE}%")
    fi
    
    # Send alert if issues found
    if [ ${#ISSUES[@]} -gt 0 ]; then
        MESSAGE="Critical issues detected:\n"
        for issue in "${ISSUES[@]}"; do
            MESSAGE="$MESSAGE\n- $issue"
        done
        send_alert "⚠️ CryptoBot Critical Alert" "$MESSAGE"
    fi
}

# ====================================
# PERFORMANCE STATS
# ====================================

performance_report() {
    echo -e "${GREEN}=========================================${NC}"
    echo -e "${GREEN}   PERFORMANCE REPORT${NC}"
    echo -e "${GREEN}=========================================${NC}"
    echo ""
    
    # Uptime
    echo -e "${BLUE}System Uptime:${NC}"
    uptime -p
    echo ""
    
    # Load average
    echo -e "${BLUE}Load Average:${NC}"
    uptime | awk -F'load average:' '{print $2}'
    echo ""
    
    # Top processes
    echo -e "${BLUE}Top CPU Processes:${NC}"
    ps aux --sort=-%cpu | head -6 | tail -5
    echo ""
    
    echo -e "${BLUE}Top Memory Processes:${NC}"
    ps aux --sort=-%mem | head -6 | tail -5
    echo ""
    
    # Disk I/O
    echo -e "${BLUE}Disk I/O:${NC}"
    iostat -x 1 2 | tail -n +4
    echo ""
}

# ====================================
# AUTO-RESTART
# ====================================

auto_restart() {
    echo "Checking services for auto-restart..."
    
    if ! pgrep -f "main.py" > /dev/null; then
        echo "Restarting main application..."
        cd $APP_DIR
        source venv/bin/activate
        nohup python main.py > output.log 2>&1 &
        echo "Main application restarted"
    fi
    
    if ! pgrep -f "telegram_bot.py" > /dev/null; then
        echo "Restarting Telegram bot..."
        cd $APP_DIR
        source venv/bin/activate
        nohup python telegram_bot.py > telegram.log 2>&1 &
        echo "Telegram bot restarted"
    fi
}

# ====================================
# MAIN MENU
# ====================================

case "$1" in
    status)
        full_status
        ;;
    watch)
        watch_status
        ;;
    services)
        check_services
        ;;
    database)
        check_database
        ;;
    api)
        check_api
        ;;
    logs)
        check_logs
        ;;
    performance)
        performance_report
        ;;
    critical)
        check_critical
        ;;
    restart)
        auto_restart
        ;;
    *)
        echo "CryptoBot Pro - System Monitor"
        echo ""
        echo "Usage: $0 {status|watch|services|database|api|logs|performance|critical|restart}"
        echo ""
        echo "Commands:"
        echo "  status       - Full system status check"
        echo "  watch        - Live monitoring (auto-refresh)"
        echo "  services     - Check service status"
        echo "  database     - Database health check"
        echo "  api          - API health check"
        echo "  logs         - Check for recent errors"
        echo "  performance  - Detailed performance report"
        echo "  critical     - Check for critical issues"
        echo "  restart      - Auto-restart stopped services"
        echo ""
        echo "Examples:"
        echo "  $0 status        # Check system status once"
        echo "  $0 watch         # Live monitoring"
        echo "  $0 critical      # Check critical issues"
        echo ""
        exit 1
        ;;
esac

exit 0
