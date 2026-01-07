"""
database.py - SQLite Database Setup for CryptoTradeBot
Creates tables for users, profiles, trades, and bot status
"""

import sqlite3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

DATABASE_FILE = 'trading_bot.db'


def get_connection():
    """Get database connection"""
    return sqlite3.connect(DATABASE_FILE)


def init_database():
    """Initialize database with all required tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # ==================== USERS TABLE ====================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT,
                telegram_username TEXT,
                referral_code TEXT UNIQUE,
                referred_by TEXT,
                subscription_status TEXT DEFAULT 'inactive',
                subscription_expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # ==================== USER PROFILES TABLE ====================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                capital REAL,
                experience TEXT,
                risk_tolerance TEXT,
                can_monitor BOOLEAN,
                selected_strategy TEXT,
                onboarding_completed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)
        
        # ==================== API KEYS TABLE ====================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                key_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                exchange TEXT NOT NULL,
                api_key TEXT NOT NULL,
                api_secret TEXT NOT NULL,
                is_testnet BOOLEAN DEFAULT 0,
                is_validated BOOLEAN DEFAULT 0,
                last_validated_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                UNIQUE(user_id, exchange)
            )
        """)
        
        # ==================== BOT STATUS TABLE ====================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bot_status (
                bot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                bot_type TEXT NOT NULL,
                status TEXT DEFAULT 'stopped',
                config TEXT,
                started_at TIMESTAMP,
                stopped_at TIMESTAMP,
                last_run TIMESTAMP,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                UNIQUE(user_id, bot_type)
            )
        """)
        
        # ==================== TRADES TABLE ====================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                bot_type TEXT NOT NULL,
                exchange TEXT,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                order_type TEXT,
                entry_price REAL,
                exit_price REAL,
                quantity REAL,
                profit_loss REAL,
                profit_loss_percent REAL,
                fee REAL,
                opened_at TIMESTAMP,
                closed_at TIMESTAMP,
                status TEXT DEFAULT 'open',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)
        
        # ==================== REFERRALS TABLE ====================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS referrals (
                referral_id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_user_id TEXT NOT NULL,
                referred_user_id TEXT NOT NULL,
                referral_code TEXT,
                status TEXT DEFAULT 'pending',
                commission_earned REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (referrer_user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (referred_user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)
        
        # ==================== PAYMENTS TABLE ====================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                tx_hash TEXT UNIQUE,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'USDT',
                payment_type TEXT,
                status TEXT DEFAULT 'pending',
                verified_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)
        
        # ==================== NOTIFICATIONS TABLE ====================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                type TEXT NOT NULL,
                title TEXT,
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)
        
        # ==================== PERFORMANCE METRICS TABLE ====================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                bot_type TEXT,
                date DATE NOT NULL,
                total_pnl REAL DEFAULT 0,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                win_rate REAL,
                total_fees REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                UNIQUE(user_id, bot_type, date)
            )
        """)
        
        # ==================== SYSTEM LOGS TABLE ====================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
            )
        """)
        
        # ==================== INDEXES ====================
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_user ON trades(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_opened ON trades(opened_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bot_status_user ON bot_status(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_user_date ON performance_metrics(user_id, date)")
        
        conn.commit()
        logger.info("✅ Database initialized successfully: trading_bot.db")
        
        # Print table info
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        logger.info(f"✅ Created {len(tables)} tables: {', '.join(t[0] for t in tables)}")
        
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()


# ==================== HELPER FUNCTIONS ====================

def save_user_profile(user_id: str, profile: dict):
    """Save user profile from onboarding"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO user_profiles 
            (user_id, capital, experience, risk_tolerance, can_monitor, 
             selected_strategy, onboarding_completed, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, 1, ?)
        """, (
            user_id,
            profile.get('capital', 0),
            profile.get('experience', 'beginner'),
            profile.get('riskTolerance', 'medium'),
            profile.get('canMonitor', False),
            profile.get('strategy', 'grid'),
            datetime.now()
        ))
        
        conn.commit()
        logger.info(f"✅ User profile saved: {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Profile save error: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()


def get_user_profile(user_id: str) -> dict:
    """Get user profile"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT capital, experience, risk_tolerance, can_monitor, selected_strategy
            FROM user_profiles
            WHERE user_id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        
        if row:
            return {
                'capital': row[0],
                'experience': row[1],
                'risk_tolerance': row[2],
                'can_monitor': row[3],
                'selected_strategy': row[4]
            }
        
        return None
        
    except Exception as e:
        logger.error(f"❌ Profile fetch error: {e}")
        return None
    
    finally:
        conn.close()


def save_trade(user_id: str, trade_data: dict) -> int:
    """Save trade to database"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO trades 
            (user_id, bot_type, exchange, symbol, side, order_type,
             entry_price, quantity, opened_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'open')
        """, (
            user_id,
            trade_data.get('bot_type'),
            trade_data.get('exchange'),
            trade_data.get('symbol'),
            trade_data.get('side'),
            trade_data.get('order_type', 'market'),
            trade_data.get('entry_price'),
            trade_data.get('quantity'),
            datetime.now()
        ))
        
        trade_id = cursor.lastrowid
        conn.commit()
        
        logger.info(f"✅ Trade saved: {trade_id}")
        return trade_id
        
    except Exception as e:
        logger.error(f"❌ Trade save error: {e}")
        conn.rollback()
        return None
    
    finally:
        conn.close()


def close_trade(trade_id: int, exit_price: float, fee: float = 0):
    """Close trade and calculate P&L"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Get trade details
        cursor.execute("""
            SELECT entry_price, quantity, side
            FROM trades
            WHERE trade_id = ? AND status = 'open'
        """, (trade_id,))
        
        row = cursor.fetchone()
        if not row:
            logger.warning(f"Trade {trade_id} not found or already closed")
            return False
        
        entry_price, quantity, side = row
        
        # Calculate P&L
        if side == 'buy':
            profit_loss = (exit_price - entry_price) * quantity - fee
        else:  # sell
            profit_loss = (entry_price - exit_price) * quantity - fee
        
        profit_loss_percent = (profit_loss / (entry_price * quantity)) * 100
        
        # Update trade
        cursor.execute("""
            UPDATE trades
            SET exit_price = ?, profit_loss = ?, profit_loss_percent = ?,
                fee = ?, closed_at = ?, status = 'closed'
            WHERE trade_id = ?
        """, (exit_price, profit_loss, profit_loss_percent, fee, datetime.now(), trade_id))
        
        conn.commit()
        
        logger.info(f"✅ Trade closed: {trade_id}, P&L: {profit_loss:.2f}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Trade close error: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()


def get_user_trades(user_id: str, limit: int = 50) -> list:
    """Get user's recent trades"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT trade_id, bot_type, symbol, side, entry_price, exit_price,
                   quantity, profit_loss, opened_at, closed_at, status
            FROM trades
            WHERE user_id = ?
            ORDER BY opened_at DESC
            LIMIT ?
        """, (user_id, limit))
        
        rows = cursor.fetchall()
        
        trades = []
        for row in rows:
            trades.append({
                'trade_id': row[0],
                'bot_type': row[1],
                'symbol': row[2],
                'side': row[3],
                'entry_price': row[4],
                'exit_price': row[5],
                'quantity': row[6],
                'profit_loss': row[7],
                'opened_at': row[8],
                'closed_at': row[9],
                'status': row[10]
            })
        
        return trades
        
    except Exception as e:
        logger.error(f"❌ Trades fetch error: {e}")
        return []
    
    finally:
        conn.close()


def update_bot_status(user_id: str, bot_type: str, status: str, config: dict = None):
    """Update bot status"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        import json
        config_json = json.dumps(config) if config else None
        
        cursor.execute("""
            INSERT OR REPLACE INTO bot_status 
            (user_id, bot_type, status, config, last_run, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id, bot_type, status, config_json,
            datetime.now(), datetime.now()
        ))
        
        conn.commit()
        logger.info(f"✅ Bot status updated: {bot_type} -> {status}")
        
    except Exception as e:
        logger.error(f"❌ Bot status update error: {e}")
        conn.rollback()
    
    finally:
        conn.close()


# ==================== RUN IF MAIN ====================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 60)
    print("Initializing CryptoTradeBot Database")
    print("=" * 60)
    
    init_database()
    
    print("\n" + "=" * 60)
    print("Database ready! File: trading_bot.db")
    print("=" * 60)
