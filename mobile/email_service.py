# email_service.py - Email Notification System
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """
    Professional email notification system
    - Welcome emails
    - Payment confirmations
    - Bot alerts
    - Performance reports
    """
    
    def __init__(self, config: Dict):
        self.smtp_server = config.get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = config.get('smtp_port', 587)
        self.sender_email = config.get('sender_email', 'noreply@cryptobot.com')
        self.sender_password = config.get('sender_password', '')
        self.sender_name = config.get('sender_name', 'CryptoTradeBot Pro')
    
    def _send_email(self, to_email: str, subject: str, html_body: str, 
                   text_body: str = None) -> bool:
        """Send email via SMTP"""
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = f"{self.sender_name} <{self.sender_email}>"
            message['To'] = to_email
            
            # Add text and HTML parts
            if text_body:
                text_part = MIMEText(text_body, 'plain')
                message.attach(text_part)
            
            html_part = MIMEText(html_body, 'html')
            message.attach(html_part)
            
            # Connect and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            logger.info(f"Email sent to {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def send_welcome_email(self, user_email: str, username: str, 
                          referral_code: str = None) -> bool:
        """Send welcome email to new user"""
        subject = "Welcome to CryptoTradeBot Pro! 🚀"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #3b82f6, #10b981); padding: 30px; text-align: center; color: white; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; }}
                .button {{ display: inline-block; padding: 15px 30px; background: #3b82f6; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .features {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; }}
                .feature {{ margin: 15px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Welcome to CryptoTradeBot Pro!</h1>
                    <p>Your intelligent crypto trading assistant</p>
                </div>
                
                <div class="content">
                    <h2>Hi {username}! 👋</h2>
                    <p>Thank you for joining CryptoTradeBot Pro. You now have access to 7 powerful trading bots designed to help you maximize your crypto portfolio.</p>
                    
                    <div class="features">
                        <h3>🤖 Your Trading Bots:</h3>
                        <div class="feature">🔄 <strong>DCA Bot</strong> - Automated dollar cost averaging</div>
                        <div class="feature">📊 <strong>Signal Bot</strong> - Technical analysis signals</div>
                        <div class="feature">💼 <strong>Portfolio Bot</strong> - Automatic rebalancing</div>
                        <div class="feature">🎯 <strong>Trailing Stop</strong> - Profit protection</div>
                        <div class="feature">⚖️ <strong>Arbitrage Bot</strong> - Cross-exchange opportunities</div>
                    </div>
                    
                    <center>
                        <a href="https://cryptobot.com/dashboard" class="button">Go to Dashboard</a>
                    </center>
                    
                    <h3>💰 Pricing & Referrals</h3>
                    <p><strong>Subscription:</strong> $39/month for full access</p>
                    <p><strong>Referral Program:</strong> Get 20% off per referral, FREE after 5 friends!</p>
                    
                    {f'<p>Your Referral Code: <strong>{referral_code}</strong></p>' if referral_code else ''}
                    
                    <h3>🚀 Getting Started</h3>
                    <ol>
                        <li>Connect your exchange API keys</li>
                        <li>Configure your first trading bot</li>
                        <li>Set your risk management preferences</li>
                        <li>Start trading!</li>
                    </ol>
                    
                    <p>Need help? Reply to this email or join our Telegram community.</p>
                </div>
                
                <div class="footer">
                    <p>© 2024 CryptoTradeBot Pro. All rights reserved.</p>
                    <p>This email was sent to {user_email}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Welcome to CryptoTradeBot Pro!
        
        Hi {username}!
        
        Thank you for joining CryptoTradeBot Pro. You now have access to 7 powerful trading bots.
        
        Visit your dashboard: https://cryptobot.com/dashboard
        
        Subscription: $39/month
        Referral Program: Get 20% off per referral, FREE after 5!
        
        {'Your Referral Code: ' + referral_code if referral_code else ''}
        
        Need help? Reply to this email.
        """
        
        return self._send_email(user_email, subject, html_body, text_body)
    
    def send_payment_confirmation(self, user_email: str, username: str, 
                                 amount: float, tx_hash: str, expires_date: str) -> bool:
        """Send payment confirmation email"""
        subject = "Payment Confirmed - Subscription Active ✅"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #10b981; padding: 30px; text-align: center; color: white; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; }}
                .receipt {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; border-left: 4px solid #10b981; }}
                .receipt-row {{ display: flex; justify-content: space-between; margin: 10px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Payment Confirmed!</h1>
                    <p>Your subscription is now active</p>
                </div>
                
                <div class="content">
                    <h2>Hi {username}!</h2>
                    <p>We've successfully verified your payment. Your CryptoTradeBot Pro subscription is now active!</p>
                    
                    <div class="receipt">
                        <h3>📋 Payment Receipt</h3>
                        <div class="receipt-row">
                            <span>Amount Paid:</span>
                            <strong>${amount:.2f} USDT</strong>
                        </div>
                        <div class="receipt-row">
                            <span>Transaction:</span>
                            <span style="font-size: 12px; color: #666;">{tx_hash[:20]}...</span>
                        </div>
                        <div class="receipt-row">
                            <span>Subscription Period:</span>
                            <strong>30 Days</strong>
                        </div>
                        <div class="receipt-row">
                            <span>Expires:</span>
                            <strong>{expires_date}</strong>
                        </div>
                    </div>
                    
                    <p>You now have full access to all trading bots and features. Start trading today!</p>
                    
                    <center>
                        <a href="https://cryptobot.com/bots" style="display: inline-block; padding: 15px 30px; background: #10b981; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0;">
                            Start Trading
                        </a>
                    </center>
                    
                    <p style="font-size: 12px; color: #666;">View transaction on Polygonscan: https://polygonscan.com/tx/{tx_hash}</p>
                </div>
                
                <div class="footer">
                    <p>© 2024 CryptoTradeBot Pro. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(user_email, subject, html_body)
    
    def send_bot_alert(self, user_email: str, username: str, bot_type: str, 
                      alert_type: str, message: str) -> bool:
        """Send bot alert notification"""
        subject = f"🔔 Bot Alert: {bot_type.upper()} - {alert_type}"
        
        alert_colors = {
            'success': '#10b981',
            'warning': '#f59e0b',
            'error': '#ef4444',
            'info': '#3b82f6'
        }
        
        color = alert_colors.get(alert_type.lower(), '#3b82f6')
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: {color}; padding: 30px; text-align: center; color: white; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; }}
                .alert {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; border-left: 4px solid {color}; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔔 Bot Alert</h1>
                    <p>{bot_type.upper()} Bot Notification</p>
                </div>
                
                <div class="content">
                    <h2>Hi {username}!</h2>
                    
                    <div class="alert">
                        <h3>{alert_type.upper()}</h3>
                        <p>{message}</p>
                        <p style="font-size: 12px; color: #666;">Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                    </div>
                    
                    <center>
                        <a href="https://cryptobot.com/bots" style="display: inline-block; padding: 15px 30px; background: {color}; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0;">
                            View Dashboard
                        </a>
                    </center>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(user_email, subject, html_body)
    
    def send_daily_report(self, user_email: str, username: str, 
                         performance_data: Dict) -> bool:
        """Send daily performance report"""
        subject = f"📊 Daily Report - {datetime.now().strftime('%B %d, %Y')}"
        
        total_pnl = performance_data.get('total_pnl', 0)
        pnl_color = '#10b981' if total_pnl >= 0 else '#ef4444'
        pnl_sign = '+' if total_pnl >= 0 else ''
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #3b82f6, #10b981); padding: 30px; text-align: center; color: white; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; }}
                .stats {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; }}
                .stat-row {{ display: flex; justify-content: space-between; margin: 15px 0; padding: 10px; border-bottom: 1px solid #eee; }}
                .big-stat {{ text-align: center; padding: 20px; background: #f0f0f0; border-radius: 8px; margin: 20px 0; }}
                .big-stat-value {{ font-size: 36px; font-weight: bold; color: {pnl_color}; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Daily Performance Report</h1>
                    <p>{datetime.now().strftime('%B %d, %Y')}</p>
                </div>
                
                <div class="content">
                    <h2>Hi {username}!</h2>
                    <p>Here's your trading performance for today:</p>
                    
                    <div class="big-stat">
                        <div style="font-size: 14px; color: #666; margin-bottom: 10px;">Total P&L</div>
                        <div class="big-stat-value">{pnl_sign}${abs(total_pnl):.2f}</div>
                    </div>
                    
                    <div class="stats">
                        <h3>📈 Trading Statistics</h3>
                        <div class="stat-row">
                            <span>Total Trades:</span>
                            <strong>{performance_data.get('total_trades', 0)}</strong>
                        </div>
                        <div class="stat-row">
                            <span>Winning Trades:</span>
                            <strong>{performance_data.get('winning_trades', 0)}</strong>
                        </div>
                        <div class="stat-row">
                            <span>Win Rate:</span>
                            <strong>{performance_data.get('win_rate', 0):.1%}</strong>
                        </div>
                        <div class="stat-row">
                            <span>Active Bots:</span>
                            <strong>{performance_data.get('active_bots', 0)}</strong>
                        </div>
                    </div>
                    
                    <center>
                        <a href="https://cryptobot.com/performance" style="display: inline-block; padding: 15px 30px; background: #3b82f6; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0;">
                            View Full Report
                        </a>
                    </center>
                    
                    <p style="font-size: 12px; color: #666;">Keep up the great work! Remember to review your risk settings regularly.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(user_email, subject, html_body)
    
    def send_subscription_expiry_warning(self, user_email: str, username: str, 
                                        days_remaining: int) -> bool:
        """Send subscription expiry warning"""
        subject = f"⚠️ Subscription Expiring in {days_remaining} Days"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #f59e0b; padding: 30px; text-align: center; color: white; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; }}
                .warning {{ background: #fff3cd; padding: 20px; margin: 20px 0; border-radius: 8px; border-left: 4px solid #f59e0b; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚠️ Subscription Expiring Soon</h1>
                </div>
                
                <div class="content">
                    <h2>Hi {username}!</h2>
                    
                    <div class="warning">
                        <p><strong>Your subscription expires in {days_remaining} days.</strong></p>
                        <p>Renew now to continue using all trading bots without interruption.</p>
                    </div>
                    
                    <p>💳 Renewal Price: $39 USDT (Polygon network)</p>
                    <p>Payment Address: <code>0xfee37e7e64d70f37f96c42375131abb57c1481c2</code></p>
                    
                    <center>
                        <a href="https://cryptobot.com/subscription" style="display: inline-block; padding: 15px 30px; background: #f59e0b; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0;">
                            Renew Subscription
                        </a>
                    </center>
                    
                    <p style="font-size: 12px; color: #666;">💡 Tip: Refer 5 friends to get FREE access!</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(user_email, subject, html_body)

# Quick send functions
def send_welcome(user_email: str, username: str, config: Dict) -> bool:
    """Quick function to send welcome email"""
    service = EmailService(config)
    return service.send_welcome_email(user_email, username)

def send_alert(user_email: str, username: str, bot_type: str, 
              alert_type: str, message: str, config: Dict) -> bool:
    """Quick function to send alert"""
    service = EmailService(config)
    return service.send_bot_alert(user_email, username, bot_type, alert_type, message)
