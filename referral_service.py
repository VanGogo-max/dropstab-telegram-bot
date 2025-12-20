"""
Referral System - $10/month with $1 discount per referral
Free after 10 referrals!
"""

import logging
from datetime import datetime
from typing import Optional
import secrets

from database import db_session, User, Referral
from config import SUBSCRIPTION_PRICE, REFERRAL_DISCOUNT, FREE_REFERRALS_NEEDED

logger = logging.getLogger(__name__)


class ReferralService:
    """Manage referral system and discounts"""
    
    def __init__(self):
        self.base_price = SUBSCRIPTION_PRICE  # $10
        self.discount_per_referral = REFERRAL_DISCOUNT  # $1
        self.free_threshold = FREE_REFERRALS_NEEDED  # 10 referrals
    
    def generate_referral_code(self, user_id: int) -> str:
        """Generate unique referral code for user"""
        try:
            user = db_session.query(User).filter_by(id=user_id).first()
            
            if not user:
                return ""
            
            # Generate code if doesn't exist
            if not user.referral_code:
                code = self._generate_unique_code()
                user.referral_code = code
                db_session.commit()
                logger.info(f"Generated referral code for user {user_id}: {code}")
            
            return user.referral_code
            
        except Exception as e:
            logger.error(f"Generate referral code error: {e}")
            return ""
    
    def _generate_unique_code(self) -> str:
        """Generate unique 8-character referral code"""
        while True:
            code = secrets.token_urlsafe(6).upper()[:8]
            
            # Check if code exists
            existing = db_session.query(User).filter_by(
                referral_code=code
            ).first()
            
            if not existing:
                return code
    
    def apply_referral_code(self, user_id: int, referral_code: str) -> bool:
        """Apply referral code when user signs up"""
        try:
            # Find referrer by code
            referrer = db_session.query(User).filter_by(
                referral_code=referral_code
            ).first()
            
            if not referrer:
                logger.warning(f"Invalid referral code: {referral_code}")
                return False
            
            # Check if user already used a referral
            user = db_session.query(User).filter_by(id=user_id).first()
            if user.referred_by:
                logger.warning(f"User {user_id} already has referrer")
                return False
            
            # Create referral relationship
            referral = Referral(
                referrer_id=referrer.id,
                referred_id=user_id,
                created_at=datetime.utcnow(),
                status='active'
            )
            db_session.add(referral)
            
            # Update user
            user.referred_by = referrer.id
            
            db_session.commit()
            
            logger.info(f"Referral applied: {referrer.id} -> {user_id}")
            
            # Give $1 discount to new user for first month
            self._apply_signup_discount(user_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Apply referral error: {e}")
            db_session.rollback()
            return False
    
    def _apply_signup_discount(self, user_id: int):
        """Give $1 discount to new user (first month $9)"""
        try:
            user = db_session.query(User).filter_by(id=user_id).first()
            if user:
                # New user pays $9 first month
                user.current_discount = 1.00
                db_session.commit()
                logger.info(f"Applied $1 signup discount to user {user_id}")
        except Exception as e:
            logger.error(f"Signup discount error: {e}")
    
    def calculate_price(self, user_id: int) -> float:
        """Calculate subscription price with referral discounts"""
        try:
            user = db_session.query(User).filter_by(id=user_id).first()
            
            if not user:
                return self.base_price
            
            # Count active referrals
            referral_count = db_session.query(Referral).filter_by(
                referrer_id=user_id,
                status='active'
            ).count()
            
            # Calculate discount ($1 per referral)
            total_discount = referral_count * self.discount_per_referral
            
            # Cap at base price (can't go below $0)
            if total_discount >= self.base_price:
                price = 0.00  # FREE!
                logger.info(f"User {user_id} has FREE subscription ({referral_count} referrals)")
            else:
                price = self.base_price - total_discount
            
            return price
            
        except Exception as e:
            logger.error(f"Calculate price error: {e}")
            return self.base_price
    
    def get_referral_stats(self, user_id: int) -> dict:
        """Get referral statistics for user"""
        try:
            # Get active referrals
            active_referrals = db_session.query(Referral).filter_by(
                referrer_id=user_id,
                status='active'
            ).all()
            
            # Calculate savings
            referral_count = len(active_referrals)
            monthly_discount = referral_count * self.discount_per_referral
            current_price = self.calculate_price(user_id)
            
            # Check if free
            is_free = (referral_count >= self.free_threshold)
            
            # Calculate how many more needed for free
            needed_for_free = max(0, self.free_threshold - referral_count)
            
            return {
                'referral_count': referral_count,
                'monthly_discount': monthly_discount,
                'current_price': current_price,
                'is_free': is_free,
                'needed_for_free': needed_for_free,
                'savings_per_year': monthly_discount * 12,
                'referral_code': self.generate_referral_code(user_id)
            }
            
        except Exception as e:
            logger.error(f"Get referral stats error: {e}")
            return {
                'referral_count': 0,
                'monthly_discount': 0,
                'current_price': self.base_price,
                'is_free': False,
                'needed_for_free': self.free_threshold,
                'savings_per_year': 0,
                'referral_code': ''
            }
    
    def deactivate_referral(self, referral_id: int) -> bool:
        """Deactivate referral (if user cancels subscription)"""
        try:
            referral = db_session.query(Referral).filter_by(
                id=referral_id
            ).first()
            
            if referral:
                referral.status = 'inactive'
                db_session.commit()
                logger.info(f"Referral {referral_id} deactivated")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Deactivate referral error: {e}")
            return False
    
    def get_referral_leaderboard(self, limit: int = 10) -> list:
        """Get top referrers"""
        try:
            from sqlalchemy import func
            
            # Count referrals per user
            leaderboard = db_session.query(
                User.id,
                User.email,
                func.count(Referral.id).label('referral_count')
            ).join(
                Referral, User.id == Referral.referrer_id
            ).filter(
                Referral.status == 'active'
            ).group_by(
                User.id
            ).order_by(
                func.count(Referral.id).desc()
            ).limit(limit).all()
            
            result = []
            for user_id, email, count in leaderboard:
                result.append({
                    'user_id': user_id,
                    'email': email,
                    'referrals': count,
                    'monthly_savings': count * self.discount_per_referral,
                    'is_free': count >= self.free_threshold
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Leaderboard error: {e}")
            return []


# Global instance
referral_service = ReferralService()
