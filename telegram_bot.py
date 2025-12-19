# telegram_bot.py - Telegram Bot Interface
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from config import config
from bot_manager import BotManager
from payment_service import PaymentService
from referral_service import ReferralService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global managers
user_managers = {}
payment_service = PaymentService(config.__dict__)

class TelegramBot:
    def __init__(self):
        self.app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
        self._register_handlers()
    
    def _register_handlers(self):
        """Register command handlers"""
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("balance", self.balance))
        self.app.add_handler(CommandHandler("bots", self.bots_menu))
        self.app.add_handler(CommandHandler("start_dca", self.start_dca))
        self.app.add_handler(CommandHandler("start_signal", self.start_signal))
        self.app.add_handler(CommandHandler("start_portfolio", self.start_portfolio))
        self.app.add_handler(CommandHandler("start_trailing", self.start_trailing))
        self.app.add_handler(CommandHandler("start_arbitrage", self.start_arbitrage))
        self.app.add_handler(CommandHandler("stop", self.stop_bot))
        self.app.add_handler(CommandHandler("status", self.status))
        self.app.add_handler(CommandHandler("performance", self.performance))
        self.app.add_handler(CommandHandler("subscription", self.subscription))
        self.app.add_handler(CommandHandler("referral", self.referral))
        self.app.add_handler(CommandHandler("payment", self.payment))
        
        # Callback handlers
        self.app.add_handler(CallbackQueryHandler(self.button_callback))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command"""
        user_id = str(update.effective_user.id)
        
        # Check for referral code
        if context.args and context.args[0].startswith('ref_'):
            referral_code = context.args[0].replace('ref_', '')
            # TODO: Process referral
            await update.message.reply_text(f"✅ Referral code {referral_code} applied!")
        
        welcome_text = f"""
🎮 **Welcome to CryptoTradeBot Pro!**

I'm your intelligent crypto trading assistant with 7 powerful bots:

🤖 **Available Bots:**
• DCA Bot - Automated dollar cost averaging
• Signal Bot - Technical analysis signals
• Portfolio Bot - Auto rebalancing
• Trailing Stop - Profit protection
• Arbitrage Bot - Cross-exchange opportunities
• Grid Bot - Grid trading strategy
• Futures Bot - Futures trading

💰 **Subscription:** $39/month
🎁 **Referral:** Get 20% off per referral, FREE after 5!

Use /help to see all commands
Use /bots to manage your trading bots
        """
        
        keyboard = [
            [InlineKeyboardButton("🤖 Start Trading", callback_data="bots_menu")],
            [InlineKeyboardButton("💳 Subscribe", callback_data="subscribe")],
            [InlineKeyboardButton("📊 Performance", callback_data="performance")],
            [InlineKeyboardButton("🎁 Get Referral Link", callback_data="referral")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command"""
        help_text = """
📚 **CryptoTradeBot Pro Commands**

**Bot Management:**
/bots - View all bots menu
/start_dca - Start DCA bot
/start_signal - Start Signal bot
/start_portfolio - Start Portfolio bot
/start_trailing - Start Trailing Stop
/start_arbitrage - Start Arbitrage bot
/stop <bot_id> - Stop specific bot
/status - View all bots status

**Account:**
/balance - Check exchange balances
/performance - View trading performance
/subscription - Subscription info
/payment <tx_hash> - Verify payment
/referral - Get referral link

**Info:**
/help - Show this help

💡 **Quick Tips:**
• Start with small amounts on testnet
• Enable risk management
• Monitor bots regularly
• Join our community for support
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def bots_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Bots management menu"""
        keyboard = [
            [InlineKeyboardButton("🔄 DCA Bot", callback_data="start_dca"),
             InlineKeyboardButton("📊 Signal Bot", callback_data="start_signal")],
            [InlineKeyboardButton("💼 Portfolio Bot", callback_data="start_portfolio"),
             InlineKeyboardButton("🎯 Trailing Stop", callback_data="start_trailing")],
            [InlineKeyboardButton("⚖️ Arbitrage Bot", callback_data="start_arbitrage"),
             InlineKeyboardButton("📈 Grid Bot", callback_data="start_grid")],
            [InlineKeyboardButton("📉 Futures Bot", callback_data="start_futures")],
            [InlineKeyboardButton("🔍 View Status", callback_data="status"),
             InlineKeyboardButton("⏹️ Stop All", callback_data="stop_all")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = "🤖 **Bot Management Center**\n\nSelect a bot to start or manage:"
        
        if update.callback_query:
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def start_dca(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start DCA bot"""
        user_id = str(update.effective_user.id)
        
        # Check subscription
        # TODO: Verify active subscription
        
        # Get or create bot manager
        if user_id not in user_managers:
            user_managers[user_id] = BotManager(user_id, config.__dict__)
        
        manager = user_managers[user_id]
        
        # Default DCA config
        dca_config = {
            'symbol': 'BTC/USDT',
            'interval_hours': 24,
            'amount_per_order': 50,
            'max_total_investment': 1000,
            'exchange': 'binance'
        }
        
        try:
            bot_id = await manager.start_dca_bot(dca_config)
            
            text = f"""
✅ **DCA Bot Started!**

📝 Configuration:
• Symbol: {dca_config['symbol']}
• Interval: {dca_config['interval_hours']} hours
• Amount per order: ${dca_config['amount_per_order']}
• Max investment: ${dca_config['max_total_investment']}

Bot ID: `{bot_id}`

Use /status to monitor progress
Use /stop {bot_id} to stop bot
            """
            await update.message.reply_text(text, parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ Error starting DCA bot: {str(e)}")
    
    async def start_signal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start Signal bot"""
        user_id = str(update.effective_user.id)
        
        if user_id not in user_managers:
            user_managers[user_id] = BotManager(user_id, config.__dict__)
        
        manager = user_managers[user_id]
        
        signal_config = {
            'symbols': ['BTC/USDT', 'ETH/USDT'],
            'timeframe': '1h',
            'auto_trade': False,
            'exchange': 'binance'
        }
        
        try:
            bot_id = await manager.start_signal_bot(signal_config)
            
            text = f"""
✅ **Signal Bot Started!**

📝 Configuration:
• Symbols: {', '.join(signal_config['symbols'])}
• Timeframe: {signal_config['timeframe']}
• Auto-trade: {'Enabled' if signal_config['auto_trade'] else 'Disabled (notifications only)'}

You'll receive trading signals based on:
• RSI (Relative Strength Index)
• MACD (Moving Average Convergence Divergence)
• Bollinger Bands
• Volume analysis

Bot ID: `{bot_id}`
            """
            await update.message.reply_text(text, parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ Error starting Signal bot: {str(e)}")
    
    async def balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check balance"""
        user_id = str(update.effective_user.id)
        
        if user_id not in user_managers:
            await update.message.reply_text("❌ No active bots. Start a bot first with /start_dca or /start_signal")
            return
        
        manager = user_managers[user_id]
        
        try:
            balances = await manager.exchange_manager.get_all_balances()
            
            text = "💰 **Your Balances:**\n\n"
            
            for exchange, balance in balances.items():
                text += f"**{exchange.upper()}:**\n"
                for currency, amounts in balance.items():
                    if isinstance(amounts, dict) and amounts.get('total', 0) > 0:
                        text += f"  • {currency}: {amounts['total']:.4f}\n"
                text += "\n"
            
            await update.message.reply_text(text, parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ Error fetching balance: {str(e)}")
    
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """View bots status"""
        user_id = str(update.effective_user.id)
        
        if user_id not in user_managers:
            await update.message.reply_text("❌ No active bots")
            return
        
        manager = user_managers[user_id]
        status = manager.get_all_bots_status()
        
        if not status:
            await update.message.reply_text("📊 No bots running")
            return
        
        text = "📊 **Bots Status:**\n\n"
        
        for bot_id, bot_info in status.items():
            status_emoji = "🟢" if bot_info['status'] == 'running' else "🔴"
            text += f"{status_emoji} **{bot_id}**\n"
            text += f"Status: {bot_info['status']}\n"
            
            if 'details' in bot_info:
                details = bot_info['details']
                if 'active' in details:
                    text += f"Active: {details['active']}\n"
                if 'total_invested' in details:
                    text += f"Invested: ${details['total_invested']:.2f}\n"
            
            text += "\n"
        
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def performance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """View performance"""
        user_id = str(update.effective_user.id)
        
        if user_id not in user_managers:
            await update.message.reply_text("❌ No trading history")
            return
        
        manager = user_managers[user_id]
        perf = await manager.get_total_performance()
        
        text = f"""
📈 **Trading Performance**

💰 Total P&L: ${perf['total_profit']:.2f}
📊 Total Trades: {perf['total_trades']}
🤖 Active Bots: {perf['active_bots']}

⚠️ Risk Status:
• Emergency Stop: {'🔴 Active' if perf['risk_status']['emergency_stop'] else '🟢 Normal'}
• Daily P&L: ${perf['risk_status']['daily_pnl']:.2f}
        """
        
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def subscription(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Subscription info"""
        # TODO: Get from database
        referral_count = 0
        
        price_info = payment_service.calculate_price(referral_count)
        
        text = f"""
💳 **Subscription Information**

📅 Base Price: ${payment_service.base_price}/month
🎁 Your Referrals: {referral_count}
💰 Your Price: ${price_info}/month

{"🎉 You have FREE access!" if price_info == 0 else f"Refer {5 - referral_count} more friends for FREE access!"}

Payment Address:
`{payment_service.payment_address}`

Network: Polygon
Token: USDT

After payment, use:
/payment <transaction_hash>
        """
        
        keyboard = [
            [InlineKeyboardButton("💳 Pay Now", url=f"https://polygonscan.com/address/{payment_service.payment_address}")],
            [InlineKeyboardButton("🎁 Get Referral Link", callback_data="referral")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def payment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Verify payment"""
        if not context.args:
            await update.message.reply_text("❌ Please provide transaction hash: /payment <tx_hash>")
            return
        
        tx_hash = context.args[0]
        user_id = str(update.effective_user.id)
        
        await update.message.reply_text("⏳ Verifying payment...")
        
        # Get expected amount
        referral_count = 0  # TODO: Get from database
        expected_amount = payment_service.calculate_price(referral_count)
        
        result = await payment_service.verify_payment(tx_hash, user_id, expected_amount)
        
        if result['verified']:
            text = f"""
✅ **Payment Verified!**

Amount: ${result['amount']}
Transaction: `{tx_hash}`

Your subscription is now active!
Expires: {(result['timestamp'] + timedelta(days=30)).strftime('%Y-%m-%d')}

Start trading with /bots
            """
            await update.message.reply_text(text, parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ Payment verification failed: {result['error']}")
    
    async def referral(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get referral link"""
        user_id = str(update.effective_user.id)
        
        # TODO: Get from database
        referral_code = f"TRADE{user_id[:6].upper()}"
        referral_count = 0
        
        discount = payment_service.calculate_price(referral_count)
        
        bot_username = (await context.bot.get_me()).username
        referral_link = f"https://t.me/{bot_username}?start=ref_{referral_code}"
        
        text = f"""
🎁 **Your Referral Program**

Your Referral Code: `{referral_code}`
Your Referral Link:
{referral_link}

📊 Stats:
• Total Referrals: {referral_count}
• Current Discount: {(payment_service.base_price - discount):.0f}%
• Your Price: ${discount}/month

💰 Rewards:
• 1 referral = 20% off ($31.20)
• 3 referrals = 50% off ($19.50)
• 5 referrals = FREE ($0)

Share your link and earn discounts!
        """
        
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def stop_bot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Stop specific bot"""
        if not context.args:
            await update.message.reply_text("❌ Please provide bot ID: /stop <bot_id>")
            return
        
        bot_id = context.args[0]
        user_id = str(update.effective_user.id)
        
        if user_id not in user_managers:
            await update.message.reply_text("❌ No active bots")
            return
        
        manager = user_managers[user_id]
        success = manager.stop_bot(bot_id)
        
        if success:
            await update.message.reply_text(f"✅ Bot `{bot_id}` stopped successfully", parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ Bot `{bot_id}` not found", parse_mode='Markdown')
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "bots_menu":
            await self.bots_menu(update, context)
        elif data == "subscribe":
            await self.subscription(update, context)
        elif data == "performance":
            await self.performance(update, context)
        elif data == "referral":
            await self.referral(update, context)
        elif data == "status":
            await self.status(update, context)
        elif data.startswith("start_"):
            await query.edit_message_text(f"Use /{data} command to start this bot")
    
    def run(self):
        """Run the bot"""
        logger.info("Starting Telegram bot...")
        self.app.run_polling()

if __name__ == "__main__":
    bot = TelegramBot()
    bot.run()
