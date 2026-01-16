"""
Email Service - Notifications & Alerts
Sends emails for bot events, trades, and errors
"""

import logging
from typing import Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)

# Try to import SendGrid
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content
    HAS_SENDGRID = True
except ImportError:
    HAS_SENDGRID = False
    logger.warning("SendGrid not installed - email notifications disabled")


class EmailService:
    """
    Email notification service using SendGrid
    Falls back to console logging if SendGrid unavailable
    """
    
    def __init__(self):
        self.sendgrid_api_key = os.getenv('SENDGRID_API_KEY', '')
        self.from_email = os.getenv('FROM_EMAIL', 'bot@cryptotradepro.com')
        self.enabled = HAS_SENDGRID and bool(self.sendgrid_api_key)
        
        if self.enabled:
            self.client = SendGridAPIClient(self.sendgrid_api_key)
            logger.info("Email service initialized with SendGrid")
        else:
            logger.warning("Email service disabled - using console logging only")
    
    def _send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str
    ) -> bool:
        """Send email via SendGrid"""
        if not self.enabled:
            logger.info(f"[EMAIL] To: {to_email} | Subject: {subject}")
            logger.info(f"[EMAIL] Content: {html_content[:200]}...")
            return True
        
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            
            response = self.client.send(message)
            
            if response.status_code == 202:
                logger.info(f"Email sent to {to_email}: {subject}")
                return True
            else:
                logger.warning(f"Email failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Email send error: {e}")
            return False
    
    def _get_user_email(self, user_id: int) -> Optional[str]:
        """Get user's email from database"""
        try:
            from database import get_connection
            
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT email
                FROM users
                WHERE user_id = ?
            """, (str(user_id),))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Get user email error: {e}")
            return None
    
    def send_bot_started(
        self,
        user_id: int,
        bot_type: str,
        exchange: str
    ) -> bool:
        """Send bot started notification"""
        try:
            email = self._get_user_email(user_id)
            if not email:
                logger.warning(f"No email for user {user_id}")
                return False
            
            subject = f"🤖 {bot_type.upper()} Bot Started"
            
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2 style="color: #00c853;">✅ Bot Started Successfully</h2>
                    <p>Your <strong>{bot_type.upper()}</strong> bot is now active on <strong>{exchange}</strong>!</p>
                    
                    <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>Bot Type:</strong> {bot_type}</p>
                        <p><strong>Exchange:</strong> {exchange}</p>
                        <p><strong>Started:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</p>
                    </div>
                    
                    <p>You'll receive notifications for all trades and important events.</p>
                    
                    <p style="color: #666; font-size: 12px; margin-top: 30px;">
                        CryptoTradeBot Pro - Automated Trading Platform
                    </p>
                </body>
            </html>
            """
            
            return self._send_email(email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Send bot started email error: {e}")
            return False
    
    def send_trade_notification(
        self,
        user_id: int,
        trade_data: dict
    ) -> bool:
        """Send trade execution notification"""
        try:
            email = self._get_user_email(user_id)
            if not email:
                return False
            
            side = trade_data.get('side', 'BUY')
            symbol = trade_data.get('symbol', 'BTC/USDT')
            price = trade_data.get('price', 0)
            quantity = trade_data.get('quantity', 0)
            bot_type = trade_data.get('bot_type', 'unknown')
            
            subject = f"📊 Trade Executed: {side} {symbol}"
            
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2 style="color: #2196f3;">💼 Trade Executed</h2>
                    <p>Your <strong>{bot_type.upper()}</strong> bot executed a trade:</p>
                    
                    <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>Side:</strong> <span style="color: {'#00c853' if side == 'BUY' else '#f44336'}">{side}</span></p>
                        <p><strong>Symbol:</strong> {symbol}</p>
                        <p><strong>Price:</strong> ${price:.2f}</p>
                        <p><strong>Quantity:</strong> {quantity:.4f}</p>
                        <p><strong>Total:</strong> ${price * quantity:.2f}</p>
                        <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</p>
                    </div>
                    
                    <p>View full details in your dashboard.</p>
                    
                    <p style="color: #666; font-size: 12px; margin-top: 30px;">
                        CryptoTradeBot Pro
                    </p>
                </body>
            </html>
            """
            
            return self._send_email(email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Send trade notification error: {e}")
            return False
    
    def send_profit_alert(
        self,
        user_id: int,
        profit: float,
        symbol: str,
        bot_type: str
    ) -> bool:
        """Send profit/loss alert"""
        try:
            email = self._get_user_email(user_id)
            if not email:
                return False
            
            is_profit = profit > 0
            emoji = "🎉" if is_profit else "📉"
            color = "#00c853" if is_profit else "#f44336"
            word = "Profit" if is_profit else "Loss"
            
            subject = f"{emoji} {word}: ${abs(profit):.2f} on {symbol}"
            
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2 style="color: {color};">{emoji} Position Closed</h2>
                    <p>Your <strong>{bot_type.upper()}</strong> bot closed a position:</p>
                    
                    <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>Symbol:</strong> {symbol}</p>
                        <p><strong>{word}:</strong> <span style="color: {color}; font-size: 24px; font-weight: bold;">${abs(profit):.2f}</span></p>
                        <p><strong>Bot:</strong> {bot_type}</p>
                        <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</p>
                    </div>
                    
                    <p>Check your dashboard for detailed performance metrics.</p>
                    
                    <p style="color: #666; font-size: 12px; margin-top: 30px;">
                        CryptoTradeBot Pro
                    </p>
                </body>
            </html>
            """
            
            return self._send_email(email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Send profit alert error: {e}")
            return False
    
    def send_error_alert(
        self,
        user_id: int,
        error_title: str,
        error_message: str
    ) -> bool:
        """Send error alert"""
        try:
            email = self._get_user_email(user_id)
            if not email:
                return False
            
            subject = f"⚠️ Alert: {error_title}"
            
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2 style="color: #ff9800;">⚠️ Bot Alert</h2>
                    <p><strong>{error_title}</strong></p>
                    
                    <div style="background: #fff3e0; padding: 15px; border-radius: 5px; border-left: 4px solid #ff9800; margin: 20px 0;">
                        <p style="margin: 0; color: #e65100;">{error_message}</p>
                    </div>
                    
                    <p>Please check your bot configuration and ensure everything is set up correctly.</p>
                    
                    <p style="color: #666; font-size: 12px; margin-top: 30px;">
                        CryptoTradeBot Pro
                    </p>
                </body>
            </html>
            """
            
            return self._send_email(email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Send error alert error: {e}")
            return False
    
    def send_daily_report(
        self,
        user_id: int,
        report_data: dict
    ) -> bool:
        """Send daily performance report"""
        try:
            email = self._get_user_email(user_id)
            if not email:
                return False
            
            total_pnl = report_data.get('total_pnl', 0)
            trades_count = report_data.get('trades_count', 0)
            win_rate = report_data.get('win_rate', 0)
            
            subject = "📈 Daily Trading Report"
            
            pnl_color = "#00c853" if total_pnl >= 0 else "#f44336"
            
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2 style="color: #2196f3;">📈 Daily Performance Report</h2>
                    <p>Here's your trading summary for today:</p>
                    
                    <div style="background: #f5f5f5; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0;">Performance Metrics</h3>
                        <p><strong>Total P&L:</strong> <span style="color: {pnl_color}; font-size: 20px; font-weight: bold;">${total_pnl:.2f}</span></p>
                        <p><strong>Trades Executed:</strong> {trades_count}</p>
                        <p><strong>Win Rate:</strong> {win_rate:.1f}%</p>
                    </div>
                    
                    <p>View detailed statistics in your dashboard.</p>
                    
                    <p style="color: #666; font-size: 12px; margin-top: 30px;">
                        CryptoTradeBot Pro - Daily Report
                    </p>
                </body>
            </html>
            """
            
            return self._send_email(email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Send daily report error: {e}")
            return False
    
    def send_welcome_email(self, user_id: int) -> bool:
        """Send welcome email to new users"""
        try:
            email = self._get_user_email(user_id)
            if not email:
                return False
            
            subject = "🎉 Welcome to CryptoTradeBot Pro!"
            
            html_content = """
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2 style="color: #2196f3;">🎉 Welcome to CryptoTradeBot Pro!</h2>
                    <p>Thank you for joining our automated trading platform.</p>
                    
                    <div style="background: #e3f2fd; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0;">Getting Started</h3>
                        <ol>
                            <li>Complete your profile setup</li>
                            <li>Connect your exchange API keys</li>
                            <li>Select your trading strategy</li>
                            <li>Start your first bot!</li>
                        </ol>
                    </div>
                    
                    <p>Our AI will recommend the best strategy based on your profile and current market conditions.</p>
                    
                    <p style="margin-top: 30px;">
                        <strong>Need help?</strong> Contact our support team anytime.
                    </p>
                    
                    <p style="color: #666; font-size: 12px; margin-top: 30px;">
                        CryptoTradeBot Pro Team
                    </p>
                </body>
            </html>
            """
            
            return self._send_email(email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Send welcome email error: {e}")
            return False


# Global instance
email_service = EmailService()
