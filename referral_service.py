# referral_service.py - Referral & Reward System
import uuid
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class ReferralService:
    """
    Referral system with progressive discounts
    - Unique referral codes
    - Track referrals and earnings
    - Progressive discount tiers
    """
    
    def __init__(self, database):
        self.db = database
        
        # Referral rewards
        self.discount_per_referral = 0.20  # 20%
        self.free_threshold = 5  # Free after 5 referrals
        self.base_subscription_price = 39
    
    def generate_referral_code(self, user_id: str) -> str:
        """Generate unique referral code"""
        # Create short, memorable code
        code = f"TRADE{uuid.uuid4().hex[:6].upper()}"
        
        # Save to database
        self.db.save_referral_code(user_id, code)
        
        logger.info(f"Generated referral code {code} for user {user_id}")
        return code
    
    def validate_referral_code(self, code: str) -> Optional[str]:
        """Validate and get referrer user_id"""
        referrer = self.db.get_referrer_by_code(code)
        
        if referrer:
            logger.info(f"Valid referral code: {code} -> User {referrer}")
            return referrer
        
        logger.warning(f"Invalid referral code: {code}")
        return None
    
    def register_referral(self, referrer_id: str, referee_id: str, code: str) -> Dict:
        """Register a new referral"""
        # Check if referee already used a referral
        existing = self.db.get_user_referral(referee_id)
        if existing:
            return {
                'success': False,
                'error': 'User already used a referral code'
            }
        
        # Check self-referral
        if referrer_id == referee_id:
            return {
                'success': False,
                'error': 'Cannot use your own referral code'
            }
        
        # Save referral
        referral_data = {
            'referrer_id': referrer_id,
            'referee_id': referee_id,
            'code': code,
            'created_at': datetime.now(),
            'status': 'pending'  # Will be 'active' after first payment
        }
        
        self.db.save_referral(referral_data)
        
        logger.info(f"Referral registered: {referrer_id} -> {referee_id}")
        
        return {
            'success': True,
            'referrer': referrer_id,
            'referee': referee_id,
            'code': code
        }
    
    def activate_referral(self, referee_id: str):
        """Activate referral after first payment"""
        referral = self.db.get_user_referral(referee_id)
        
        if referral and referral['status'] == 'pending':
            self.db.update_referral_status(referee_id, 'active')
            
            # Update referrer's count
            referrer_id = referral['referrer_id']
            count = self.get_referral_count(referrer_id)
            
            logger.info(f"Referral activated for {referee_id}. Referrer {referrer_id} now has {count} referrals")
    
    def get_referral_count(self, user_id: str) -> int:
        """Get active referral count"""
        referrals = self.db.get_user_referrals(user_id, status='active')
        return len(referrals)
    
    def calculate_discount(self, referral_count: int) -> Dict:
        """Calculate current discount based on referrals"""
        if referral_count >= self.free_threshold:
            discount_percent = 1.0  # 100% = FREE
            final_price = 0
        else:
            discount_percent = min(referral_count * self.discount_per_referral, 0.95)
            final_price = self.base_subscription_price * (1 - discount_percent)
        
        savings = self.base_subscription_price - final_price
        
        return {
            'referral_count': referral_count,
            'discount_percent': discount_percent * 100,
            'original_price': self.base_subscription_price,
            'final_price': round(final_price, 2),
            'monthly_savings': round(savings, 2),
            'yearly_savings': round(savings * 12, 2),
            'is_free': referral_count >= self.free_threshold
        }
    
    def get_referral_stats(self, user_id: str) -> Dict:
        """Get detailed referral statistics"""
        referrals = self.db.get_user_referrals(user_id)
        active_referrals = [r for r in referrals if r['status'] == 'active']
        pending_referrals = [r for r in referrals if r['status'] == 'pending']
        
        discount = self.calculate_discount(len(active_referrals))
        referrals_to_free = max(0, self.free_threshold - len(active_referrals))
        
        return {
            'user_id': user_id,
            'total_referrals': len(referrals),
            'active_referrals': len(active_referrals),
            'pending_referrals': len(pending_referrals),
            'referral_code': self.db.get_user_referral_code(user_id),
            'current_discount': discount,
            'referrals_to_free': referrals_to_free,
            'next_tier_benefit': self._get_next_tier_benefit(len(active_referrals))
        }
    
    def _get_next_tier_benefit(self, current_count: int) -> Optional[Dict]:
        """Get benefit of next referral"""
        if current_count >= self.free_threshold:
            return None
        
        current_discount = self.calculate_discount(current_count)
        next_discount = self.calculate_discount(current_count + 1)
        
        return {
            'referrals_needed': 1,
            'additional_savings': round(
                next_discount['monthly_savings'] - current_discount['monthly_savings'], 
                2
            ),
            'new_price': next_discount['final_price']
        }
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get top referrers"""
        all_users = self.db.get_all_users()
        
        leaderboard = []
        for user in all_users:
            count = self.get_referral_count(user['id'])
            if count > 0:
                leaderboard.append({
                    'user_id': user['id'],
                    'username': user.get('username', 'Anonymous'),
                    'referral_count': count,
                    'discount': self.calculate_discount(count)
                })
        
        # Sort by referral count
        leaderboard.sort(key=lambda x: x['referral_count'], reverse=True)
        
        return leaderboard[:limit]
    
    def get_referral_link(self, user_id: str, platform: str = 'web') -> str:
        """Generate referral link"""
        code = self.db.get_user_referral_code(user_id)
        
        if not code:
            code = self.generate_referral_code(user_id)
        
        base_urls = {
            'web': 'https://yourapp.com/signup?ref=',
            'telegram': 'https://t.me/yourbot?start=ref_',
            'mobile': 'yourapp://signup?ref='
        }
        
        base_url = base_urls.get(platform, base_urls['web'])
        return f"{base_url}{code}"
    
    def get_referral_performance(self, user_id: str) -> Dict:
        """Get referral performance over time"""
        referrals = self.db.get_user_referrals(user_id)
        
        if not referrals:
            return {
                'total_value_generated': 0,
                'conversion_rate': 0,
                'timeline': []
            }
        
        # Calculate total value generated
        active_count = len([r for r in referrals if r['status'] == 'active'])
        total_value = active_count * self.base_subscription_price  # Value brought to platform
        
        # Timeline of referrals
        timeline = []
        cumulative = 0
        for referral in sorted(referrals, key=lambda x: x['created_at']):
            if referral['status'] == 'active':
                cumulative += 1
                timeline.append({
                    'date': referral['created_at'].strftime('%Y-%m-%d'),
                    'cumulative_referrals': cumulative,
                    'discount_at_time': self.calculate_discount(cumulative)['discount_percent']
                })
        
        return {
            'total_value_generated': total_value,
            'conversion_rate': active_count / len(referrals) if referrals else 0,
            'timeline': timeline,
            'milestones_reached': self._get_milestones_reached(active_count)
        }
    
    def _get_milestones_reached(self, count: int) -> List[str]:
        """Get milestones user has reached"""
        milestones = []
        
        if count >= 1:
            milestones.append("🎉 First referral - 20% discount unlocked")
        if count >= 3:
            milestones.append("🔥 3 referrals - 50% discount unlocked")
        if count >= 5:
            milestones.append("⭐ 5 referrals - FREE access unlocked!")
        
        return milestones
    
    def send_referral_notification(self, referrer_id: str, referee_name: str):
        """Notify user of new referral"""
        count = self.get_referral_count(referrer_id)
        discount = self.calculate_discount(count)
        
        message = f"""
🎉 New Referral!

{referee_name} just signed up using your referral code!

Your stats:
• Total referrals: {count}
• Current discount: {discount['discount_percent']:.0f}%
• Monthly price: ${discount['final_price']:.2f}
• You save: ${discount['monthly_savings']:.2f}/month

{f"🎯 Just {self.free_threshold - count} more for FREE access!" if count < self.free_threshold else "⭐ You have FREE access!"}
        """
        
        return message
