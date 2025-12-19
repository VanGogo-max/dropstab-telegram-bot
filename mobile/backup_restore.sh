#!/bin/bash
# backup_restore.sh - Automated Backup & Restore System

# Configuration
BACKUP_DIR="/home/cryptobot/backups"
DB_NAME="cryptobot"
DB_USER="cryptobot"
APP_DIR="/home/cryptobot/cryptobot"
RETENTION_DAYS=30

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ====================================
# BACKUP FUNCTIONS
# ====================================

backup_database() {
    echo -e "${YELLOW}Starting database backup...${NC}"
    
    DATE=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.sql"
    
    # Create backup directory if not exists
    mkdir -p $BACKUP_DIR
    
    # Backup PostgreSQL database
    pg_dump -U $DB_USER $DB_NAME > $BACKUP_FILE
    
    if [ $? -eq 0 ]; then
        # Compress backup
        gzip $BACKUP_FILE
        echo -e "${GREEN}✓ Database backup completed: ${BACKUP_FILE}.gz${NC}"
        
        # Calculate size
        SIZE=$(du -h "${BACKUP_FILE}.gz" | cut -f1)
        echo -e "${GREEN}  Size: $SIZE${NC}"
        
        return 0
    else
        echo -e "${RED}✗ Database backup failed${NC}"
        return 1
    fi
}

backup_environment() {
    echo -e "${YELLOW}Backing up environment files...${NC}"
    
    DATE=$(date +%Y%m%d_%H%M%S)
    ENV_BACKUP="$BACKUP_DIR/env_backup_$DATE.tar.gz"
    
    # Backup .env and config files
    tar -czf $ENV_BACKUP -C $APP_DIR .env config.py
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Environment backup completed${NC}"
        return 0
    else
        echo -e "${RED}✗ Environment backup failed${NC}"
        return 1
    fi
}

backup_logs() {
    echo -e "${YELLOW}Backing up logs...${NC}"
    
    DATE=$(date +%Y%m%d_%H%M%S)
    LOG_BACKUP="$BACKUP_DIR/logs_backup_$DATE.tar.gz"
    
    # Backup log files
    tar -czf $LOG_BACKUP -C $APP_DIR cryptobot.log telegram.log 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Logs backup completed${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠ No logs to backup${NC}"
        return 0
    fi
}

backup_redis() {
    echo -e "${YELLOW}Backing up Redis data...${NC}"
    
    DATE=$(date +%Y%m%d_%H%M%S)
    REDIS_BACKUP="$BACKUP_DIR/redis_backup_$DATE.rdb"
    
    # Trigger Redis save
    redis-cli SAVE
    
    # Copy Redis dump
    cp /var/lib/redis/dump.rdb $REDIS_BACKUP
    
    if [ $? -eq 0 ]; then
        gzip $REDIS_BACKUP
        echo -e "${GREEN}✓ Redis backup completed${NC}"
        return 0
    else
        echo -e "${RED}✗ Redis backup failed${NC}"
        return 1
    fi
}

full_backup() {
    echo -e "${GREEN}===========================================${NC}"
    echo -e "${GREEN}  CRYPTOBOT PRO - FULL BACKUP${NC}"
    echo -e "${GREEN}===========================================${NC}"
    echo ""
    
    START_TIME=$(date +%s)
    
    # Run all backups
    backup_database
    DB_STATUS=$?
    
    backup_environment
    ENV_STATUS=$?
    
    backup_logs
    LOG_STATUS=$?
    
    backup_redis
    REDIS_STATUS=$?
    
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    echo ""
    echo -e "${GREEN}===========================================${NC}"
    echo -e "${GREEN}  BACKUP SUMMARY${NC}"
    echo -e "${GREEN}===========================================${NC}"
    
    if [ $DB_STATUS -eq 0 ]; then
        echo -e "${GREEN}✓ Database: Success${NC}"
    else
        echo -e "${RED}✗ Database: Failed${NC}"
    fi
    
    if [ $ENV_STATUS -eq 0 ]; then
        echo -e "${GREEN}✓ Environment: Success${NC}"
    else
        echo -e "${RED}✗ Environment: Failed${NC}"
    fi
    
    if [ $LOG_STATUS -eq 0 ]; then
        echo -e "${GREEN}✓ Logs: Success${NC}"
    else
        echo -e "${RED}✗ Logs: Failed${NC}"
    fi
    
    if [ $REDIS_STATUS -eq 0 ]; then
        echo -e "${GREEN}✓ Redis: Success${NC}"
    else
        echo -e "${RED}✗ Redis: Failed${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}Duration: ${DURATION}s${NC}"
    echo -e "${YELLOW}Backup location: $BACKUP_DIR${NC}"
    
    # Calculate total backup size
    TOTAL_SIZE=$(du -sh $BACKUP_DIR | cut -f1)
    echo -e "${YELLOW}Total backup size: $TOTAL_SIZE${NC}"
    
    echo ""
}

# ====================================
# RESTORE FUNCTIONS
# ====================================

restore_database() {
    if [ -z "$1" ]; then
        echo -e "${RED}Error: Please specify backup file${NC}"
        echo "Usage: $0 restore-db <backup_file>"
        return 1
    fi
    
    BACKUP_FILE=$1
    
    if [ ! -f "$BACKUP_FILE" ]; then
        echo -e "${RED}Error: Backup file not found: $BACKUP_FILE${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}WARNING: This will overwrite the current database!${NC}"
    read -p "Are you sure? (yes/no): " CONFIRM
    
    if [ "$CONFIRM" != "yes" ]; then
        echo "Restore cancelled"
        return 0
    fi
    
    echo -e "${YELLOW}Restoring database...${NC}"
    
    # Check if file is gzipped
    if [[ $BACKUP_FILE == *.gz ]]; then
        gunzip -c $BACKUP_FILE | psql -U $DB_USER $DB_NAME
    else
        psql -U $DB_USER $DB_NAME < $BACKUP_FILE
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Database restored successfully${NC}"
        return 0
    else
        echo -e "${RED}✗ Database restore failed${NC}"
        return 1
    fi
}

restore_environment() {
    if [ -z "$1" ]; then
        echo -e "${RED}Error: Please specify backup file${NC}"
        return 1
    fi
    
    BACKUP_FILE=$1
    
    if [ ! -f "$BACKUP_FILE" ]; then
        echo -e "${RED}Error: Backup file not found: $BACKUP_FILE${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}Restoring environment files...${NC}"
    
    tar -xzf $BACKUP_FILE -C $APP_DIR
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Environment restored successfully${NC}"
        return 0
    else
        echo -e "${RED}✗ Environment restore failed${NC}"
        return 1
    fi
}

list_backups() {
    echo -e "${GREEN}===========================================${NC}"
    echo -e "${GREEN}  AVAILABLE BACKUPS${NC}"
    echo -e "${GREEN}===========================================${NC}"
    echo ""
    
    if [ ! -d "$BACKUP_DIR" ]; then
        echo -e "${YELLOW}No backups found${NC}"
        return
    fi
    
    echo "Database Backups:"
    ls -lh $BACKUP_DIR/db_backup_*.sql.gz 2>/dev/null | awk '{print $9, "(" $5 ")"}'
    
    echo ""
    echo "Environment Backups:"
    ls -lh $BACKUP_DIR/env_backup_*.tar.gz 2>/dev/null | awk '{print $9, "(" $5 ")"}'
    
    echo ""
    echo "Redis Backups:"
    ls -lh $BACKUP_DIR/redis_backup_*.rdb.gz 2>/dev/null | awk '{print $9, "(" $5 ")"}'
    
    echo ""
}

# ====================================
# CLEANUP FUNCTIONS
# ====================================

cleanup_old_backups() {
    echo -e "${YELLOW}Cleaning up backups older than $RETENTION_DAYS days...${NC}"
    
    # Find and delete old backups
    DELETED=$(find $BACKUP_DIR -name "*.gz" -mtime +$RETENTION_DAYS -delete -print | wc -l)
    
    echo -e "${GREEN}✓ Deleted $DELETED old backup(s)${NC}"
}

# ====================================
# AUTOMATED BACKUP
# ====================================

setup_cron() {
    echo -e "${YELLOW}Setting up automated daily backups...${NC}"
    
    SCRIPT_PATH=$(readlink -f "$0")
    CRON_JOB="0 2 * * * $SCRIPT_PATH backup >> $BACKUP_DIR/backup.log 2>&1"
    
    # Add to crontab
    (crontab -l 2>/dev/null | grep -v "$SCRIPT_PATH"; echo "$CRON_JOB") | crontab -
    
    echo -e "${GREEN}✓ Automated backup scheduled for 2:00 AM daily${NC}"
    echo -e "${YELLOW}Logs will be saved to: $BACKUP_DIR/backup.log${NC}"
}

# ====================================
# CLOUD BACKUP (Optional)
# ====================================

upload_to_cloud() {
    echo -e "${YELLOW}Uploading latest backup to cloud...${NC}"
    
    # Find latest backup
    LATEST_DB=$(ls -t $BACKUP_DIR/db_backup_*.sql.gz 2>/dev/null | head -1)
    
    if [ -z "$LATEST_DB" ]; then
        echo -e "${RED}No backups found to upload${NC}"
        return 1
    fi
    
    # Example: Upload to AWS S3 (uncomment and configure)
    # aws s3 cp $LATEST_DB s3://your-bucket/backups/
    
    # Example: Upload to Google Drive (using rclone)
    # rclone copy $LATEST_DB gdrive:backups/
    
    echo -e "${YELLOW}Cloud upload not configured. See script for examples.${NC}"
}

# ====================================
# MAIN SCRIPT
# ====================================

case "$1" in
    backup)
        full_backup
        cleanup_old_backups
        ;;
    backup-db)
        backup_database
        ;;
    backup-env)
        backup_environment
        ;;
    restore-db)
        restore_database "$2"
        ;;
    restore-env)
        restore_environment "$2"
        ;;
    list)
        list_backups
        ;;
    cleanup)
        cleanup_old_backups
        ;;
    setup-cron)
        setup_cron
        ;;
    cloud)
        upload_to_cloud
        ;;
    *)
        echo "CryptoBot Pro - Backup & Restore Tool"
        echo ""
        echo "Usage: $0 {backup|backup-db|backup-env|restore-db|restore-env|list|cleanup|setup-cron|cloud}"
        echo ""
        echo "Commands:"
        echo "  backup        - Full backup (database, environment, logs, redis)"
        echo "  backup-db     - Backup database only"
        echo "  backup-env    - Backup environment files only"
        echo "  restore-db    - Restore database from backup"
        echo "  restore-env   - Restore environment from backup"
        echo "  list          - List available backups"
        echo "  cleanup       - Remove old backups (>30 days)"
        echo "  setup-cron    - Setup automated daily backups"
        echo "  cloud         - Upload latest backup to cloud"
        echo ""
        echo "Examples:"
        echo "  $0 backup"
        echo "  $0 restore-db $BACKUP_DIR/db_backup_20240115_100000.sql.gz"
        echo "  $0 list"
        echo ""
        exit 1
        ;;
esac

exit 0
