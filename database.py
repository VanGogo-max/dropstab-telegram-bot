# database.py - Database Models & Operations
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import logging
from config import config

logger = logging.getLogger(__name__)

Base = declarative_base()

# Models
class User(Base):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password_hash = Column(String)
    telegram_id = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    exchanges = relationship("ExchangeConnection", back_populates="user")
    bots = relationship("BotInstance", back_populates="user")
    referrals_given = relationship("Referral", foreign_keys="Referral.referee_id", back_populates="referee")
    referrals_received = relationship("Referral", foreign_keys="Referral.referrer_id", back_populates="referrer")

class Subscription(Base):
    __tablename__ = 'subscriptions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'))
    status = Column(String)  # active, expired, cancelled
    price_paid = Column(Float)
    referral_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime)
    payment_tx = Column(String, nullable=True)
    
    user = relationship("User", back_populates="subscription")
    payments = relationship("Payment", back_populates="subscription")

class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True)
    subscription_id = Column(Integer, ForeignKey('subscriptions.id'))
    amount = Column(Float)
    tx_hash = Column(String, unique=True)
    status = Column(String)  # pending, verified, failed
    created_at = Column(DateTime, default=datetime.now)
    verified_at = Column(DateTime, nullable=True)
    
    subscription = relationship("Subscription", back_populates="payments")

class Referral(Base):
    __tablename__ = 'referrals'
    
    id = Column(Integer, primary_key=True)
    referrer_id = Column(String, ForeignKey('users.id'))
    referee_id = Column(String, ForeignKey('users.id'))
    code = Column(String)
    status = Column(String)  # pending, active
    created_at = Column(DateTime, default=datetime.now)
    activated_at = Column(DateTime, nullable=True)
    
    referrer = relationship("User", foreign_keys=[referrer_id], back_populates="referrals_received")
    referee = relationship("User", foreign_keys=[referee_id], back_populates="referrals_given")

class ReferralCode(Base):
    __tablename__ = 'referral_codes'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'))
    code = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.now)

class ExchangeConnection(Base):
    __tablename__ = 'exchange_connections'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'))
    exchange_name = Column(String)
    api_key_encrypted = Column(String)
    api_secret_encrypted = Column(String)
    testnet = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    
    user = relationship("User", back_populates="exchanges")

class BotInstance(Base):
    __tablename__ = 'bot_instances'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'))
    bot_type = Column(String)  # dca, signal, portfolio, trailing, arbitrage
    bot_id = Column(String)
    config = Column(JSON)
    status = Column(String)  # running, stopped, error
    created_at = Column(DateTime, default=datetime.now)
    started_at = Column(DateTime, nullable=True)
    stopped_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="bots")
    trades = relationship("Trade", back_populates="bot")

class Trade(Base):
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True)
    bot_instance_id = Column(Integer, ForeignKey('bot_instances.id'))
    exchange = Column(String)
    symbol = Column(String)
    side = Column(String)  # buy, sell
    order_type = Column(String)  # market, limit
    amount = Column(Float)
    price = Column(Float)
    cost = Column(Float)
    profit = Column(Float, nullable=True)
    status = Column(String)  # pending, executed, failed
    order_id = Column(String, nullable=True)
    executed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    bot = relationship("BotInstance", back_populates="trades")

class Performance(Base):
    __tablename__ = 'performance'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'))
    bot_type = Column(String)
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    total_profit = Column(Float, default=0)
    total_loss = Column(Float, default=0)
    win_rate = Column(Float, default=0)
    updated_at = Column(DateTime, default=datetime.now)

# Database manager
class Database:
    def __init__(self, database_url: str = None):
        self.database_url = database_url or config.DATABASE_URL
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(self.engine)
        logger.info("Database tables created")
    
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()
    
    # User operations
    def create_user(self, user_data: dict):
        """Create new user"""
        session = self.get_session()
        try:
            user = User(**user_data)
            session.add(user)
            session.commit()
            logger.info(f"User created: {user.id}")
            return user
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating user: {e}")
            return None
        finally:
            session.close()
    
    def get_user(self, user_id: str):
        """Get user by ID"""
        session = self.get_session()
        try:
            return session.query(User).filter(User.id == user_id).first()
        finally:
            session.close()
    
    def get_user_by_telegram(self, telegram_id: str):
        """Get user by Telegram ID"""
        session = self.get_session()
        try:
            return session.query(User).filter(User.telegram_id == telegram_id).first()
        finally:
            session.close()
    
    # Subscription operations
    def create_subscription(self, subscription_data: dict):
        """Create subscription"""
        session = self.get_session()
        try:
            subscription = Subscription(**subscription_data)
            session.add(subscription)
            session.commit()
            return subscription
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating subscription: {e}")
            return None
        finally:
            session.close()
    
    def get_active_subscription(self, user_id: str):
        """Get active subscription"""
        session = self.get_session()
        try:
            return session.query(Subscription).filter(
                Subscription.user_id == user_id,
                Subscription.status == 'active'
            ).first()
        finally:
            session.close()
    
    # Payment operations
    def save_payment(self, payment_data: dict):
        """Save payment record"""
        session = self.get_session()
        try:
            payment = Payment(**payment_data)
            session.add(payment)
            session.commit()
            return payment
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving payment: {e}")
            return None
        finally:
            session.close()
    
    def get_payment_by_tx(self, tx_hash: str):
        """Get payment by transaction hash"""
        session = self.get_session()
        try:
            return session.query(Payment).filter(Payment.tx_hash == tx_hash).first()
        finally:
            session.close()
    
    # Referral operations
    def save_referral_code(self, user_id: str, code: str):
        """Save referral code"""
        session = self.get_session()
        try:
            ref_code = ReferralCode(user_id=user_id, code=code)
            session.add(ref_code)
            session.commit()
            return ref_code
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving referral code: {e}")
            return None
        finally:
            session.close()
    
    def get_referrer_by_code(self, code: str):
        """Get referrer by code"""
        session = self.get_session()
        try:
            ref_code = session.query(ReferralCode).filter(ReferralCode.code == code).first()
            return ref_code.user_id if ref_code else None
        finally:
            session.close()
    
    def save_referral(self, referral_data: dict):
        """Save referral relationship"""
        session = self.get_session()
        try:
            referral = Referral(**referral_data)
            session.add(referral)
            session.commit()
            return referral
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving referral: {e}")
            return None
        finally:
            session.close()
    
    def get_user_referrals(self, user_id: str, status: str = None):
        """Get user's referrals"""
        session = self.get_session()
        try:
            query = session.query(Referral).filter(Referral.referrer_id == user_id)
            if status:
                query = query.filter(Referral.status == status)
            return query.all()
        finally:
            session.close()
    
    def get_user_referral(self, referee_id: str):
        """Get referral used by user"""
        session = self.get_session()
        try:
            return session.query(Referral).filter(Referral.referee_id == referee_id).first()
        finally:
            session.close()
    
    def update_referral_status(self, referee_id: str, status: str):
        """Update referral status"""
        session = self.get_session()
        try:
            referral = session.query(Referral).filter(Referral.referee_id == referee_id).first()
            if referral:
                referral.status = status
                referral.activated_at = datetime.now()
                session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating referral status: {e}")
        finally:
            session.close()
    
    def get_user_referral_code(self, user_id: str):
        """Get user's referral code"""
        session = self.get_session()
        try:
            ref_code = session.query(ReferralCode).filter(ReferralCode.user_id == user_id).first()
            return ref_code.code if ref_code else None
        finally:
            session.close()
    
    # Bot operations
    def save_bot_instance(self, bot_data: dict):
        """Save bot instance"""
        session = self.get_session()
        try:
            bot = BotInstance(**bot_data)
            session.add(bot)
            session.commit()
            return bot
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving bot instance: {e}")
            return None
        finally:
            session.close()
    
    def get_user_bots(self, user_id: str):
        """Get user's bots"""
        session = self.get_session()
        try:
            return session.query(BotInstance).filter(BotInstance.user_id == user_id).all()
        finally:
            session.close()
    
    # Trade operations
    def save_trade(self, trade_data: dict):
        """Save trade"""
        session = self.get_session()
        try:
            trade = Trade(**trade_data)
            session.add(trade)
            session.commit()
            return trade
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving trade: {e}")
            return None
        finally:
            session.close()
    
    def get_all_users(self):
        """Get all users"""
        session = self.get_session()
        try:
            return session.query(User).all()
        finally:
            session.close()

# Initialize database
db = Database()

if __name__ == "__main__":
    # Create tables
    db.create_tables()
    print("Database initialized successfully!")
