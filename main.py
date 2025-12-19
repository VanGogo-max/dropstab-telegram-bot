# main.py - Application Entry Point
import asyncio
import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config import config
from bot_manager import BotManager
from payment_service import PaymentService
from referral_service import ReferralService

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Global services
bot_managers = {}  # user_id -> BotManager
payment_service = None
referral_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    logger.info(f"Starting {config.APP_NAME} v{config.VERSION}")
    
    # Validate config
    try:
        config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise
    
    # Initialize services
    global payment_service, referral_service
    payment_service = PaymentService(config.__dict__)
    # referral_service = ReferralService(database)  # Initialize with DB
    
    logger.info("Services initialized successfully")
    
    yield
    
    # Cleanup
    logger.info("Shutting down...")
    for manager in bot_managers.values():
        manager.stop_all_bots()
    logger.info("Shutdown complete")

# Create FastAPI app
app = FastAPI(
    title=config.APP_NAME,
    version=config.VERSION,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": config.VERSION,
        "active_users": len(bot_managers)
    }

# User Management
@app.post("/api/user/register")
async def register_user(
    username: str,
    email: str,
    password: str,
    referral_code: str = None
):
    """Register new user"""
    # TODO: Implement user registration
    return {"message": "User registered successfully"}

@app.post("/api/user/login")
async def login(username: str, password: str):
    """User login"""
    # TODO: Implement authentication
    return {"token": "jwt-token-here"}

# Bot Management
@app.post("/api/bots/dca/start")
async def start_dca_bot(
    user_id: str,
    symbol: str,
    interval_hours: int = 24,
    amount_per_order: float = 50
):
    """Start DCA bot"""
    if user_id not in bot_managers:
        bot_managers[user_id] = BotManager(user_id, config.__dict__)
    
    manager = bot_managers[user_id]
    
    dca_config = {
        'symbol': symbol,
        'interval_hours': interval_hours,
        'amount_per_order': amount_per_order,
        'exchange': 'binance'
    }
    
    bot_id = await manager.start_dca_bot(dca_config)
    
    return {
        "success": True,
        "bot_id": bot_id,
        "config": dca_config
    }

@app.post("/api/bots/signal/start")
async def start_signal_bot(
    user_id: str,
    symbols: list,
    auto_trade: bool = False
):
    """Start Signal bot"""
    if user_id not in bot_managers:
        bot_managers[user_id] = BotManager(user_id, config.__dict__)
    
    manager = bot_managers[user_id]
    
    signal_config = {
        'symbols': symbols,
        'auto_trade': auto_trade,
        'exchange': 'binance'
    }
    
    bot_id = await manager.start_signal_bot(signal_config)
    
    return {
        "success": True,
        "bot_id": bot_id,
        "config": signal_config
    }

@app.post("/api/bots/portfolio/start")
async def start_portfolio_bot(
    user_id: str,
    allocation: dict
):
    """Start Portfolio bot"""
    if user_id not in bot_managers:
        bot_managers[user_id] = BotManager(user_id, config.__dict__)
    
    manager = bot_managers[user_id]
    
    portfolio_config = {
        'target_allocation': allocation,
        'exchange': 'binance'
    }
    
    bot_id = await manager.start_portfolio_bot(portfolio_config)
    
    return {
        "success": True,
        "bot_id": bot_id,
        "config": portfolio_config
    }

@app.post("/api/bots/trailing/start")
async def start_trailing_bot(
    user_id: str,
    symbol: str,
    entry_price: float,
    amount: float
):
    """Start Trailing Stop bot"""
    if user_id not in bot_managers:
        bot_managers[user_id] = BotManager(user_id, config.__dict__)
    
    manager = bot_managers[user_id]
    
    trailing_config = {
        'symbol': symbol,
        'exchange': 'binance'
    }
    
    bot_id = await manager.start_trailing_bot(symbol, entry_price, amount, trailing_config)
    
    return {
        "success": True,
        "bot_id": bot_id
    }

@app.post("/api/bots/arbitrage/start")
async def start_arbitrage_bot(
    user_id: str,
    symbols: list
):
    """Start Arbitrage bot"""
    if user_id not in bot_managers:
        bot_managers[user_id] = BotManager(user_id, config.__dict__)
    
    manager = bot_managers[user_id]
    
    arbitrage_config = {
        'symbols': symbols
    }
    
    bot_id = await manager.start_arbitrage_bot(arbitrage_config)
    
    return {
        "success": True,
        "bot_id": bot_id
    }

@app.post("/api/bots/{bot_id}/stop")
async def stop_bot(user_id: str, bot_id: str):
    """Stop specific bot"""
    if user_id not in bot_managers:
        raise HTTPException(status_code=404, detail="User not found")
    
    manager = bot_managers[user_id]
    success = manager.stop_bot(bot_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    return {"success": True, "bot_id": bot_id}

@app.get("/api/bots/status")
async def get_bots_status(user_id: str):
    """Get all bots status"""
    if user_id not in bot_managers:
        return {"bots": {}}
    
    manager = bot_managers[user_id]
    status = manager.get_all_bots_status()
    
    return {"bots": status}

@app.get("/api/performance")
async def get_performance(user_id: str):
    """Get overall performance"""
    if user_id not in bot_managers:
        return {"error": "User not found"}
    
    manager = bot_managers[user_id]
    performance = await manager.get_total_performance()
    
    return performance

# Payment endpoints
@app.post("/api/payment/verify")
async def verify_payment(
    user_id: str,
    tx_hash: str,
    expected_amount: float
):
    """Verify USDT payment"""
    result = await payment_service.verify_payment(tx_hash, user_id, expected_amount)
    
    if result['verified']:
        # Activate subscription
        # TODO: Save to database
        return {
            "success": True,
            "message": "Payment verified and subscription activated",
            "data": result
        }
    else:
        raise HTTPException(status_code=400, detail=result['error'])

@app.get("/api/subscription/price")
async def get_subscription_price(referral_count: int = 0):
    """Get subscription price"""
    price = payment_service.calculate_price(referral_count)
    
    return {
        "base_price": payment_service.base_price,
        "referral_count": referral_count,
        "discount": referral_count * payment_service.referral_discount * 100,
        "final_price": price,
        "is_free": referral_count >= payment_service.max_referrals_for_free
    }

# Referral endpoints
@app.get("/api/referral/code")
async def get_referral_code(user_id: str):
    """Get user's referral code"""
    # TODO: Implement with database
    return {"code": "TRADE123ABC"}

@app.get("/api/referral/stats")
async def get_referral_stats(user_id: str):
    """Get referral statistics"""
    # TODO: Implement with database
    return {
        "total_referrals": 0,
        "active_referrals": 0,
        "discount": 0
    }

# Admin endpoints
@app.get("/api/admin/stats")
async def admin_stats(password: str):
    """Admin statistics"""
    if password != config.ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    return {
        "total_users": len(bot_managers),
        "active_bots": sum(m.active_bots_count for m in bot_managers.values()),
        "version": config.VERSION
    }

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower()
    )5
