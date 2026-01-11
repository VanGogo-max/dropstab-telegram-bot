
"""
telegram_alerts.py - Admin Telegram Notifications
Sends automatic alerts to admin when errors occur or users report issues
"""

import logging
import requests
from datetime import datetime
from typing import Optional, Dict, List
import os

logger = logging.getLogger(__name__)


class TelegramAlerts:
    """
    Telegram notification system for admins
    
    Features:
    - Auto alerts when errors occur
    - User feedback notifications
    - Error logs with details
    - Simple admin commands
    
    Setup:
    1. Create Telegram bot with @BotFather
    2. Get bot token
    3. Get your chat ID (send message to bot, then check)
    4. Add to .env:
       TELEGRAM_BOT_TOKEN=your_token
       ADMIN_TELEGRAM_CHAT_ID=your_chat_id
    """
    
    def __init__(self, bot_token: str = None, admin_chat_id: str = None):
        # Get from environment or parameters
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.admin_chat_id = admin_chat_id or os.getenv('ADMIN_TELEGRAM_CHAT_ID')
        
        # Validate
        if not self.bot_token or not self.admin_chat_id:
            logger.warning(
                "Telegram alerts not configured. "
                "Set TELEGRAM_BOT_TOKEN and ADMIN_TELEGRAM_CHAT_ID in .env"
            )
            self.enabled = False
        else:
            self.enabled = True
            logger.info("Telegram alerts enabled")
        
        # API endpoint
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def send_message(
        self,
        message: str,
        chat_id: str = None,
        parse_mode: str = 'HTML'
    ) -> bool:
        """
        Send Telegram message
        
        Args:
            message: Message text
            chat_id: Recipient chat ID (defaults to admin)
            parse_mode: 'HTML' or 'Markdown'
        
        Returns:
            True if sent successfully
        """
        if not self.enabled:
            return False
        
        try:
            url = f"{self.api_url}/sendMessage"
            
            data = {
                'chat_id': chat_id or self.admin_chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                return True
            else:
                logger.error(f"Telegram send failed: {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"Telegram error: {e}")
            return False
    
    def send_error_alert(
        self,
        user_id: str,
        bot_type: str,
        error: Exception,
        context: Dict = None
    ) -> bool:
        """
        Send error alert to admin
        
        Args:
            user_id: User who experienced error
            bot_type: Bot that crashed
            error: Exception object
            context: Additional context (dict)
        """
        error_message = f"""
🚨 <b>НОВА ГРЕШКА!</b>

👤 <b>Потребител:</b> {user_id}
🤖 <b>Бот:</b> {bot_type}
❌ <b>Грешка:</b> {type(error).__name__}
💬 <b>Съобщение:</b> {str(error)}
🕐 <b>Време:</b> {datetime.now().strftime('%H:%M:%S %d.%m.%Y')}
"""
        
        if context:
            error_message += f"\n📋 <b>Контекст:</b>\n"
            for key, value in context.items():
                error_message += f"  • {key}: {value}\n"
        
        error_message += f"\n<i>Виж детайли в admin dashboard</i>"
        
        return self.send_message(error_message)
    
    def send_user_feedback(
        self,
        user_id: str,
        feedback_type: str,
        message: str,
        user_email: str = None
    ) -> bool:
        """
        Send user feedback notification to admin
        
        Args:
            user_id: User who sent feedback
            feedback_type: Type (bug, feature_request, other)
            message: Feedback message
            user_email: User's email (optional)
        """
        type_emoji = {
            'bug': '🐛',
            'feature_request': '💡',
            'other': '💬'
        }
        
        emoji = type_emoji.get(feedback_type, '📝')
        
        feedback_message = f"""
{emoji} <b>USER FEEDBACK</b>

👤 <b>От:</b> {user_email or user_id}
📂 <b>Тип:</b> {feedback_type}
🕐 <b>Време:</b> {datetime.now().strftime('%H:%M:%S %d.%m.%Y')}

💬 <b>Съобщение:</b>
{message}

<i>Отговори в admin dashboard</i>
"""
        
        return self.send_message(feedback_message)
    
    def send_signal_notification(
        self,
        symbol: str,
        direction: str,
        entry_price: float,
        user_id: str = None
    ) -> bool:
        """
        Notify when signal is executed
        
        Args:
            symbol: Trading pair
            direction: long/short
            entry_price: Entry price
            user_id: User (optional)
        """
        direction_emoji = '🟢' if direction == 'long' else '🔴'
        
        message = f"""
{direction_emoji} <b>SIGNAL EXECUTED</b>

📊 <b>Символ:</b> {symbol}
📈 <b>Посока:</b> {direction.upper()}
💰 <b>Цена:</b> ${entry_price:,.2f}
"""
        
        if user_id:
            message += f"👤 <b>Потребител:</b> {user_id}\n"
        
        message += f"🕐 <b>Време:</b> {datetime.now().strftime('%H:%M:%S')}"
        
        return self.send_message(message)
    
    def send_position_closed(
        self,
        symbol: str,
        pnl: float,
        entry_price: float,
        exit_price: float,
        user_id: str = None
    ) -> bool:
        """
        Notify when position closes
        
        Args:
            symbol: Trading pair
            pnl: Profit/Loss amount
            entry_price: Entry price
            exit_price: Exit price
            user_id: User (optional)
        """
        pnl_emoji = '💰' if pnl > 0 else '📉'
        pnl_sign = '+' if pnl >= 0 else ''
        
        message = f"""
{pnl_emoji} <b>ПОЗИЦИЯ ЗАТВОРЕНА</b>

📊 <b>Символ:</b> {symbol}
💵 <b>P&L:</b> {pnl_sign}${pnl:.2f}
📍 <b>Entry:</b> ${entry_price:,.2f}
📍 <b>Exit:</b> ${exit_price:,.2f}
"""
        
        if user_id:
            message += f"👤 <b>Потребител:</b> {user_id}\n"
        
        message += f"🕐 <b>Време:</b> {datetime.now().strftime('%H:%M:%S')}"
        
        return self.send_message(message)
    
    def send_daily_summary(self, stats: Dict) -> bool:
        """
        Send daily performance summary
        
        Args:
            stats: Dict with daily statistics
        """
        message = f"""
📊 <b>ДНЕВЕН ОТЧЕТ</b>

📅 <b>Дата:</b> {datetime.now().strftime('%d.%m.%Y')}

💰 <b>Обща печалба:</b> ${stats.get('total_pnl', 0):.2f}
📈 <b>Сделки днес:</b> {stats.get('total_trades', 0)}
✅ <b>Печеливши:</b> {stats.get('winning_trades', 0)}
❌ <b>Загубени:</b> {stats.get('losing_trades', 0)}
📊 <b>Win Rate:</b> {stats.get('win_rate', 0):.1f}%

👥 <b>Активни потребители:</b> {stats.get('active_users', 0)}
🐛 <b>Грешки днес:</b> {stats.get('errors_today', 0)}
💬 <b>Feedback днес:</b> {stats.get('feedback_today', 0)}
"""
        
        return self.send_message(message)
    
    def send_subscription_alert(
        self,
        user_id: str,
        user_email: str,
        action: str,
        amount: float = None
    ) -> bool:
        """
        Notify about subscription events
        
        Args:
            user_id: User ID
            user_email: User email
            action: 'subscribed', 'cancelled', 'renewed'
            amount: Payment amount (optional)
        """
        action_emoji = {
            'subscribed': '🎉',
            'cancelled': '😔',
            'renewed': '🔄'
        }
        
        emoji = action_emoji.get(action, '📝')
        
        message = f"""
{emoji} <b>SUBSCRIPTION {action.upper()}</b>

👤 <b>Потребител:</b> {user_email}
🆔 <b>ID:</b> {user_id}
"""
        
        if amount:
            message += f"💰 <b>Сума:</b> ${amount:.2f}\n"
        
        message += f"🕐 <b>Време:</b> {datetime.now().strftime('%H:%M:%S %d.%m.%Y')}"
        
        return self.send_message(message)
    
    def send_custom_alert(self, title: str, message: str) -> bool:
        """
        Send custom alert
        
        Args:
            title: Alert title
            message: Alert message
        """
        alert = f"""
⚠️ <b>{title}</b>

{message}

🕐 <b>Време:</b> {datetime.now().strftime('%H:%M:%S %d.%m.%Y')}
"""
        
        return self.send_message(alert)
    
    def test_connection(self) -> bool:
        """
        Test Telegram connection
        
        Sends a test message to admin
        """
        if not self.enabled:
            logger.error("Telegram not configured")
            return False
        
        test_message = """
✅ <b>TELEGRAM ALERTS TEST</b>

Свързването работи! Сега ще получаваш:
• 🚨 Известия за грешки
• 💬 User feedback
• 📊 Дневни отчети
• 💰 Subscription уведомления

<i>Тествано на {}</i>
""".format(datetime.now().strftime('%H:%M:%S %d.%m.%Y'))
        
        success = self.send_message(test_message)
        
        if success:
            logger.info("✅ Telegram test successful")
        else:
            logger.error("❌ Telegram test failed")
        
        return success


# Global instance (singleton)
_telegram_alerts_instance = None


def get_telegram_alerts() -> TelegramAlerts:
    """
    Get global TelegramAlerts instance (singleton)
    
    Usage:
        from telegram_alerts import get_telegram_alerts
        
        alerts = get_telegram_alerts()
        alerts.send_error_alert(user_id, bot_type, error)
    """
    global _telegram_alerts_instance
    
    if _telegram_alerts_instance is None:
        _telegram_alerts_instance = TelegramAlerts()
    
    return _telegram_alerts_instance


# Convenience functions
def send_error_alert(user_id: str, bot_type: str, error: Exception, context: Dict = None):
    """Quick function to send error alert"""
    alerts = get_telegram_alerts()
    return alerts.send_error_alert(user_id, bot_type, error, context)


def send_user_feedback(user_id: str, feedback_type: str, message: str, user_email: str = None):
    """Quick function to send user feedback"""
    alerts = get_telegram_alerts()
    return alerts.send_user_feedback(user_id, feedback_type, message, user_email)


def send_signal_notification(symbol: str, direction: str, entry_price: float, user_id: str = None):
    """Quick function to send signal notification"""
    alerts = get_telegram_alerts()
    return alerts.send_signal_notification(symbol, direction, entry_price, user_id)


def send_position_closed(symbol: str, pnl: float, entry_price: float, exit_price: float, user_id: str = None):
    """Quick function to send position closed notification"""
    alerts = get_telegram_alerts()
    return alerts.send_position_closed(symbol, pnl, entry_price, exit_price, user_id)


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test with environment variables
    # Make sure to set in .env:
    # TELEGRAM_BOT_TOKEN=your_bot_token
    # ADMIN_TELEGRAM_CHAT_ID=your_chat_id
    
    alerts = TelegramAlerts()
    
    # Test connection
    print("Testing Telegram connection...")
    success = alerts.test_connection()
    
    if success:
        print("✅ Test successful! Check your Telegram")
        
        # Test error alert
        try:
            raise ValueError("This is a test error")
        except Exception as e:
            alerts.send_error_alert(
                user_id='test_user',
                bot_type='test_bot',
                error=e,
                context={'test': True}
            )
        
        # Test user feedback
        alerts.send_user_feedback(
            user_id='test_user',
            feedback_type='bug',
            message='This is a test feedback message',
            user_email='test@example.com'
        )
        
        # Test signal notification
        alerts.send_signal_notification(
            symbol='BTC/USDT',
            direction='long',
            entry_price=43000.0,
            user_id='test_user'
        )
        
        print("✅ All test messages sent!")
    else:
        print("❌ Test failed. Check your .env configuration")

══════════════════════════════════════════════════
