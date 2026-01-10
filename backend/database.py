
"""
database.py - SQLite Database Setup for CryptoTradeBot
UPDATED: Добавени таблици за Signal Grid, Demo Mode, Feedback System
"""

import sqlite3
from datetime import datetime
import logging
import json

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
                mode TEXT DEFAULT 'demo',
                real_mode_activated_at TIMESTAMP,
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
        
        # ==================== TELEGRAM SIGNALS TABLE (NEW!) ====================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS telegram_signals (
                signal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_name TEXT NOT NULL,
                channel_id TEXT,
                raw_text TEXT NOT NULL,
                parsed_symbol TEXT,
                parsed_direction TEXT,
                parsed_entry_price REAL,
                parsed_stop_loss REAL,
                parsed_take_profits TEXT,
                confidence REAL,
                executed BOOLEAN DEFAULT 0,
                execution_result TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                executed_at DATETIME
            )
        """)
        
        # ==================== DEMO PORTFOLIOS TABLE (NEW!) ====================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS demo_portfolios (
                portfolio_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                balance_usdt REAL DEFAULT 10000.0,
                positions TEXT,
                trades TEXT,
                total_pnl REAL DEFAULT 0.0,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_reset DATETIME,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                UNIQUE(user_id)
            )
        """)
        
        # ==================== ERROR LOGS TABLE (NEW!) ====================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS error_logs (
                error_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                bot_type TEXT NOT NULL,
                error_type TEXT NOT NULL,
                error_message TEXT NOT NULL,
                stack_trace TEXT,
                context TEXT,
                severity TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'open',
                resolved_at DATETIME,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
            )
        """)
        
        # ==================== USER FEEDBACK TABLE (NEW!) ====================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                type TEXT NOT NULL,
                message TEXT NOT NULL,
                screenshot_url TEXT,
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'open',
                admin_response TEXT,
                responded_at DATETIME,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
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
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_channel ON telegram_signals(channel_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_errors_user ON error_logs(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_errors_status ON error_logs(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_user ON user_feedback(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_status ON user_feedback(status)")
        
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


def get_user_mode(user_id: str) -> str:
    """Get user's current mode (demo/real)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT mode FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else 'demo'
    except Exception as e:
        logger.error(f"Error getting user mode: {e}")
        return 'demo'
    finally:
        conn.close()


def switch_user_mode(user_id: str, new_mode: str) -> bool:
    """Switch user between demo/real mode"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE users 
            SET mode = ?,
                real_mode_activated_at = CASE 
                    WHEN ? = 'real' AND real_mode_activated_at IS NULL 
                    THEN ? 
                    ELSE real_mode_activated_at 
                END,
                updated_at = ?
            WHERE user_id = ?
        """, (new_mode, new_mode, datetime.now(), datetime.now(), user_id))
        
        conn.commit()
        logger.info(f"✅ User {user_id} switched to {new_mode} mode")
        return True
    except Exception as e:
        logger.error(f"Error switching mode: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def save_telegram_signal(channel_name: str, raw_text: str, parsed_data: dict = None):
    """Save Telegram signal to database"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO telegram_signals 
            (channel_name, raw_text, parsed_symbol, parsed_direction, 
             parsed_entry_price, parsed_stop_loss, parsed_take_profits, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            channel_name,
            raw_text,
            parsed_data.get('symbol') if parsed_data else None,
            parsed_data.get('direction') if parsed_data else None,
            parsed_data.get('entry_price') if parsed_data else None,
            parsed_data.get('stop_loss') if parsed_data else None,
            json.dumps(parsed_data.get('take_profits', [])) if parsed_data else None,
            parsed_data.get('confidence', 0.0) if parsed_data else 0.0
        ))
        
        signal_id = cursor.lastrowid
        conn.commit()
        logger.info(f"✅ Signal saved: {signal_id}")
        return signal_id
    except Exception as e:
        logger.error(f"Error saving signal: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()


def log_error(user_id: str, bot_type: str, error: Exception, context: dict = None):
    """Log error to database"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        import traceback
        
        cursor.execute("""
            INSERT INTO error_logs 
            (user_id, bot_type, error_type, error_message, stack_trace, context, severity)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            bot_type,
            type(error).__name__,
            str(error),
            traceback.format_exc(),
            json.dumps(context) if context else None,
            'high' if 'critical' in str(error).lower() else 'medium'
        ))
        
        error_id = cursor.lastrowid
        conn.commit()
        logger.info(f"✅ Error logged: {error_id}")
        return error_id
    except Exception as e:
        logger.error(f"Error logging error: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()


def save_user_feedback(user_id: str, feedback_type: str, message: str, screenshot_url: str = None):
    """Save user feedback to database"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO user_feedback 
            (user_id, type, message, screenshot_url)
            VALUES (?, ?, ?, ?)
        """, (user_id, feedback_type, message, screenshot_url))
        
        feedback_id = cursor.lastrowid
        conn.commit()
        logger.info(f"✅ Feedback saved: {feedback_id}")
        return feedback_id
    except Exception as e:
        logger.error(f"Error saving feedback: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()


# ==================== DEMO MODE FUNCTIONS ====================

def get_demo_portfolio(user_id: str) -> dict:
    """Get user's demo portfolio"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT balance_usdt, positions, trades, total_pnl, 
                   total_trades, winning_trades, losing_trades
            FROM demo_portfolios
            WHERE user_id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        
        if row:
            return {
                'balance_usdt': row[0],
                'positions': json.loads(row[1]) if row[1] else {},
                'trades': json.loads(row[2]) if row[2] else [],
                'total_pnl': row[3],
                'total_trades': row[4],
                'winning_trades': row[5],
                'losing_trades': row[6]
            }
        else:
            # Create new demo portfolio
            cursor.execute("""
                INSERT INTO demo_portfolios (user_id)
                VALUES (?)
            """, (user_id,))
            conn.commit()
            
            return {
                'balance_usdt': 10000.0,
                'positions': {},
                'trades': [],
                'total_pnl': 0.0,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0
            }
    except Exception as e:
        logger.error(f"Error getting demo portfolio: {e}")
        return None
    finally:
        conn.close()


def update_demo_portfolio(user_id: str, portfolio: dict):
    """Update demo portfolio"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE demo_portfolios
            SET balance_usdt = ?,
                positions = ?,
                trades = ?,
                total_pnl = ?,
                total_trades = ?,
                winning_
