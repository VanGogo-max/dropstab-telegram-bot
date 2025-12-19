# payment_service.py - USDT Polygon Payment System
from web3 import Web3
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class PaymentService:
    """
    USDT Polygon payment processing
    - Monthly subscriptions ($39/month)
    - Automatic payment verification
    - Referral discount tracking
    """
    
    def __init__(self, config: Dict):
        # Polygon RPC
        self.w3 = Web3(Web3.HTTPProvider(config.get('polygon_rpc', 'https://polygon-rpc.com')))
        
        # Payment wallet
        self.payment_address = '0xfee37e7e64d70f37f96c42375131abb57c1481c2'
        
        # USDT contract on Polygon
        self.usdt_contract_address = '0xc2132D05D31c914a87C6611C10748AEb04B58e8F'
        
        # Pricing
        self.base_price = 39  # $39/month
        self.referral_discount = 0.20  # 20% per referral
        self.max_referrals_for_free = 5  # Free after 5 referrals
        
        # USDT Contract ABI (minimal)
        self.usdt_abi = [
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function"
            }
        ]
        
        self.usdt_contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.usdt_contract_address),
            abi=self.usdt_abi
        )
    
    def calculate_price(self, referral_count: int) -> float:
        """Calculate subscription price based on referrals"""
        if referral_count >= self.max_referrals_for_free:
            return 0.0  # Free!
        
        discount = referral_count * self.referral_discount
        discount = min(discount, 0.95)  # Max 95% discount
        
        final_price = self.base_price * (1 - discount)
        return round(final_price, 2)
    
    async def verify_payment(self, tx_hash: str, user_id: str, 
                           expected_amount: float) -> Dict:
        """Verify USDT payment transaction"""
        try:
            # Get transaction
            tx = self.w3.eth.get_transaction(tx_hash)
            
            if not tx:
                return {
                    'verified': False,
                    'error': 'Transaction not found'
                }
            
            # Get transaction receipt
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            
            if not receipt or receipt['status'] != 1:
                return {
                    'verified': False,
                    'error': 'Transaction failed'
                }
            
            # Verify recipient
            if tx['to'].lower() != self.usdt_contract_address.lower():
                return {
                    'verified': False,
                    'error': 'Wrong contract address'
                }
            
            # Decode transfer event
            transfer_amount = self._decode_transfer_amount(receipt)
            
            # USDT has 6 decimals
            actual_amount = transfer_amount / 10**6
            
            # Verify amount (allow 1% difference for fees/rounding)
            if abs(actual_amount - expected_amount) > expected_amount * 0.01:
                return {
                    'verified': False,
                    'error': f'Amount mismatch: expected ${expected_amount}, got ${actual_amount}'
                }
            
            # Verify recipient address
            transfer_to = self._decode_transfer_recipient(receipt)
            if transfer_to.lower() != self.payment_address.lower():
                return {
                    'verified': False,
                    'error': 'Wrong recipient address'
                }
            
            logger.info(f"Payment verified: ${actual_amount} from user {user_id}")
            
            return {
                'verified': True,
                'amount': actual_amount,
                'tx_hash': tx_hash,
                'block': receipt['blockNumber'],
                'timestamp': datetime.now()
            }
        
        except Exception as e:
            logger.error(f"Payment verification error: {e}")
            return {
                'verified': False,
                'error': str(e)
            }
    
    def _decode_transfer_amount(self, receipt: Dict) -> int:
        """Decode transfer amount from transaction logs"""
        for log in receipt['logs']:
            if log['address'].lower() == self.usdt_contract_address.lower():
                # Transfer event signature
                if log['topics'][0].hex() == '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef':
                    # Amount is in data field
                    amount = int(log['data'].hex(), 16)
                    return amount
        return 0
    
    def _decode_transfer_recipient(self, receipt: Dict) -> str:
        """Decode recipient address from transaction logs"""
        for log in receipt['logs']:
            if log['address'].lower() == self.usdt_contract_address.lower():
                if len(log['topics']) >= 3:
                    # Recipient is in topics[2]
                    recipient = '0x' + log['topics'][2].hex()[-40:]
                    return recipient
        return ''
    
    def create_subscription(self, user_id: str, referral_count: int = 0) -> Dict:
        """Create new subscription"""
        price = self.calculate_price(referral_count)
        expires_at = datetime.now() + timedelta(days=30)
        
        return {
            'user_id': user_id,
            'price': price,
            'referral_count': referral_count,
            'discount_percent': referral_count * self.referral_discount * 100,
            'created_at': datetime.now(),
            'expires_at': expires_at,
            'status': 'pending',
            'payment_address': self.payment_address,
            'payment_instructions': self._get_payment_instructions(price)
        }
    
    def _get_payment_instructions(self, amount: float) -> str:
        """Generate payment instructions"""
        if amount == 0:
            return "✅ You have FREE access (5+ referrals)!"
        
        return f"""
💳 Payment Instructions:

1. Send exactly ${amount} USDT on Polygon network
2. To address: {self.payment_address}
3. Use Polygon (MATIC) network only!
4. After payment, submit your transaction hash

⚠️ Important:
- Use USDT on Polygon (not Ethereum or BSC)
- Check address carefully
- Keep transaction hash for verification
        """
    
    def activate_subscription(self, user_id: str, payment_data: Dict) -> Dict:
        """Activate subscription after payment"""
        return {
            'user_id': user_id,
            'status': 'active',
            'activated_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(days=30),
            'payment_tx': payment_data['tx_hash'],
            'amount_paid': payment_data['amount']
        }
    
    def check_subscription_status(self, expires_at: datetime) -> str:
        """Check if subscription is still active"""
        now = datetime.now()
        
        if now > expires_at:
            return 'expired'
        elif now > expires_at - timedelta(days=3):
            return 'expiring_soon'
        else:
            return 'active'
    
    def get_renewal_info(self, user_id: str, current_expires: datetime, 
                        referral_count: int) -> Dict:
        """Get renewal information"""
        price = self.calculate_price(referral_count)
        days_remaining = (current_expires - datetime.now()).days
        
        return {
            'user_id': user_id,
            'current_expires': current_expires,
            'days_remaining': max(0, days_remaining),
            'renewal_price': price,
            'referral_count': referral_count,
            'savings': self.base_price - price,
            'payment_address': self.payment_address
        }
    
    def calculate_earnings_potential(self, referral_count: int) -> Dict:
        """Calculate potential savings/earnings from referrals"""
        savings_per_month = []
        
        for refs in range(referral_count + 1, min(referral_count + 6, 6)):
            price = self.calculate_price(refs)
            savings = self.base_price - price
            savings_per_month.append({
                'referrals': refs,
                'price': price,
                'savings': savings
            })
        
        return {
            'current_price': self.calculate_price(referral_count),
            'current_savings': self.base_price - self.calculate_price(referral_count),
            'potential_savings': savings_per_month,
            'referrals_to_free': max(0, self.max_referrals_for_free - referral_count)
        }
