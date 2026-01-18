"""Email notification service for trading bot alerts."""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime


class EmailService:
    """Service for sending email notifications about trades and alerts."""
    
    def __init__(self, config: dict):
        """
        Initialize email service.
        
        Args:
            config: Email configuration dictionary
        """
        self.smtp_server = config.get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = config.get('smtp_port', 587)
        self.sender_email = config.get('sender_email')
        self.sender_password = config.get('sender_password')
        self.recipient_email = config.get('recipient_email')
        self.enabled = config.get('enabled', False)
        
        self.logger = logging.getLogger(__name__)
        
    def send_trade_notification(self, trade_info: dict) -> bool:
        """
        Send notification about executed trade.
        
        Args:
            trade_info: Dictionary with trade details
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            return False
            
        subject = f"Trade Executed: {trade_info.get('side', 'N/A')} {trade_info.get('symbol', 'N/A')}"
        
        body = f"""
        Trade Notification
        ==================
        
        Symbol: {trade_info.get('symbol', 'N/A')}
        Side: {trade_info.get('side', 'N/A')}
        Price: {trade_info.get('price', 'N/A')}
        Amount: {trade_info.get('amount', 'N/A')}
        Total: {trade_info.get('total', 'N/A')}
        Time: {trade_info.get('timestamp', datetime.now())}
        
        Strategy: {trade_info.get('strategy', 'N/A')}
        """
        
        return self._send_email(subject, body)
        
    def send_alert(self, alert_type: str, message: str, priority: str = 'normal') -> bool:
        """
        Send alert notification.
        
        Args:
            alert_type: Type of alert (error, warning, info)
            message: Alert message
            priority: Priority level (low, normal, high)
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            return False
            
        emoji_map = {
            'error': '🔴',
            'warning': '⚠️',
            'info': 'ℹ️',
            'success': '✅'
        }
        
        emoji = emoji_map.get(alert_type.lower(), '📧')
        subject = f"{emoji} CryptoBot Alert: {alert_type.upper()}"
        
        body = f"""
        Alert Notification
        ==================
        
        Type: {alert_type}
        Priority: {priority}
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Message:
        {message}
        """
        
        return self._send_email(subject, body)
        
    def send_daily_report(self, report_data: dict) -> bool:
        """
        Send daily performance report.
        
        Args:
            report_data: Dictionary with daily statistics
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            return False
            
        subject = f"Daily Trading Report - {datetime.now().strftime('%Y-%m-%d')}"
        
        body = f"""
        Daily Trading Report
        ====================
        
        Date: {report_data.get('date', datetime.now().strftime('%Y-%m-%d'))}
        
        Performance:
        - Total Trades: {report_data.get('total_trades', 0)}
        - Winning Trades: {report_data.get('winning_trades', 0)}
        - Losing Trades: {report_data.get('losing_trades', 0)}
        - Win Rate: {report_data.get('win_rate', 0):.2f}%
        
        Financial:
        - Total Profit/Loss: {report_data.get('total_pnl', 0):.2f}
        - Largest Win: {report_data.get('largest_win', 0):.2f}
        - Largest Loss: {report_data.get('largest_loss', 0):.2f}
        - Average Trade: {report_data.get('avg_trade', 0):.2f}
        
        Portfolio:
        - Starting Balance: {report_data.get('start_balance', 0):.2f}
        - Ending Balance: {report_data.get('end_balance', 0):.2f}
        - Return: {report_data.get('return_pct', 0):.2f}%
        """
        
        return self._send_email(subject, body)
        
    def _send_email(self, subject: str, body: str) -> bool:
        """
        Internal method to send email.
        
        Args:
            subject: Email subject
            body: Email body
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not all([self.sender_email, self.sender_password, self.recipient_email]):
            self.logger.error("Email configuration incomplete")
            return False
            
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
                
            self.logger.info(f"Email sent successfully: {subject}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False
