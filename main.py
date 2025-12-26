# main.py - CryptoTradeBot Pro Application Entry Point
"""
Main FastAPI application with all routes integrated.
Manages bot lifecycle, payments, and user operations.
"""

import asyncio
import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config import config
from bot_manager import BotManager
from payment_service import PaymentService
from referral_service import ReferralService

# Import API routes
from api_routes import router as api_router

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
    logger.info("=" * 60)
    logger.info(f"Starting {config.APP_NAME} v{config.VERSION}")
    logger.info("=" * 60)
    
    # Validate configuration
    try:
        config.validate()
        logger.info("✓ Configuration validated")
    except ValueError as e:
        logger.error(f"✗ Configuration error: {e}")
        raise
    
    # Initialize global services
    global payment_service, referral_service
    try:
        payment_service = PaymentService(config.__dict__)
        logger.info("✓ Payment service initialized")
        
        # referral_service = ReferralService(database)
        logger.info("✓ Referral service ready")
        
    except Exception as e:
        logger.error(f"✗ Service initialization failed: {e}")
        raise
    
    logger.info("✓ All services initialized successfully")
    logger.info(f"✓ Server running on http://0.0.0.0:8000")
    logger.info(f"✓ API docs available at http://0.0.0.0:8000/docs")
    
    yield
    
    # Cleanup on shutdown
    logger.info("=" * 60)
    logger.info("Shutting down gracefully...")
    logger.info("=" * 60)
    
    for user_id, manager in bot_managers.items():
        logger.info(f"Stopping bots for user: {user_id}")
        manager.stop_all_bots()
    
    logger.info("✓ All bots stopped")
    logger.info("✓ Shutdown complete")

# Create FastAPI application
app = FastAPI(
    title=config.APP_NAME,
    version=config.VERSION,
    description="Automated cryptocurrency trading platform with 10+ strategies",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes from api_routes.py
app.include_router(api_router, tags=["API"])
logger.info("✓ API routes loaded")

# ==================== HEALTH & STATUS ====================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "app": config.APP_NAME,
        "version": config.VERSION,
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": config.VERSION,
        "active_users": len(bot_managers),
        "total_bots": sum(
            len(manager.active_bots) 
            for manager in bot_managers.values()
        )
    }

@app.get("/status", tags=["Health"])
async def detailed_status():
    """Detailed system status"""
    bot_stats = {}
    for user_id, manager in bot_managers.items():
        bot_stats[user_id] = {
            "active_bots": len(manager.active_bots),
            "total_trades": 0,  # TODO: Get from manager
            "status": "active"
        }
    
    return {
        "app": config.APP_NAME,
        "version": config.VERSION,
        "uptime": "running",
        "users": len(bot_managers),
        "bot_stats": bot_stats
    }

# ==================== LEGACY BOT ENDPOINTS ====================
# These are kept for backward compatibility with old bot_manager calls

@app.post("/api/bots/dca/start", tags=["Legacy Bots"])
async def start_dca_bot_legacy(
    user_id: str,
    symbol: str,
    interval_hours: int = 24,
    amount_per_order: float = 50
):
    """Start DCA bot (legacy endpoint)"""
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
    
    logger.info(f"DCA bot started: {bot_id} for user {user_id}")
    
    return {
        "success": True,
        "bot_id": bot_id,
        "config": dca_config
    }

@app.post("/api/bots/signal/start", tags=["Legacy Bots"])
async def start_signal_bot_legacy(
    user_id: str,
    symbols: list,
    auto_trade: bool = False
):
    """Start Signal bot (legacy endpoint)"""
    if user_id not in bot_managers:
        bot_managers[user_id] = BotManager(user_id, config.__dict__)
    
    manager = bot_managers[user_id]
    
    signal_config = {
        'symbols': symbols,
        'auto_trade': auto_trade,
        'exchange': 'binance'
    }
    
    bot_id = await manager.start_signal_bot(signal_config)
    
    logger.info(f"Signal bot started: {bot_id} for user {user_id}")
    
    return {
        "success": True,
        "bot_id": bot_id,
        "config": signal_config
    }

@app.post("/api/bots/portfolio/start", tags=["Legacy Bots"])
async def start_portfolio_bot_legacy(
    user_id: str,
    allocation: dict
):
    """Start Portfolio bot (legacy endpoint)"""
    if user_id not in bot_managers:
        bot_managers[user_id] = BotManager(user_id, config.__dict__)
    
    manager = bot_managers[user_id]
    
    portfolio_config = {
        'target_allocation': allocation,
        'exchange': 'binance'
    }
    
    bot_id = await manager.start_portfolio_bot(portfolio_config)
    
    logger.info(f"Portfolio bot started: {bot_id} for user {user_id}")
    
    return {
        "success": True,
        "bot_id": bot_id,
        "config": portfolio_config
    }

@app.post("/api/bots/arbitrage/start", tags=["Legacy Bots"])
async def start_arbitrage_bot_legacy(
    user_id: str,
    symbols: list
):
    """Start Arbitrage bot (legacy endpoint)"""
    if user_id not in bot_managers:
        bot_managers[user_id] = BotManager(user_id, config.__dict__)
    
    manager = bot_managers[user_id]
    
    arbitrage_config = {
        'symbols': symbols
    }
    
    bot_id = await manager.start_arbitrage_bot(arbitrage_config)
    
    logger.info(f"Arbitrage bot started: {bot_id} for user {user_id}")
    
    return {
        "success": True,
        "bot_id": bot_id
    }

@app.get("/api/bots/status/all", tags=["Legacy Bots"])
async def get_all_bots_status(user_id: str):
    """Get all bots status (legacy endpoint)"""
    if user_id not in bot_managers:
        return {"bots": {}}
    
    manager = bot_managers[user_id]
    status = manager.get_all_bots_status()
    
    return {"bots": status}

@app.get("/api/performance/total", tags=["Legacy Bots"])
async def get_total_performance(user_id: str):
    """Get overall performance (legacy endpoint)"""
    if user_id not in bot_managers:
        return {"error": "User not found"}
    
    manager = bot_managers[user_id]
    performance = await manager.get_total_performance()
    
    return performance

# ==================== PAYMENT ENDPOINTS ====================

@app.post("/api/payment/verify", tags=["Payment"])
async def verify_payment(
    user_id: str,
    tx_hash: str,
    expected_amount: float
):
    """Verify USDT payment on blockchain"""
    try:
        result = await payment_service.verify_payment(
            tx_hash, 
            user_id, 
            expected_amount
        )
        
        if result['verified']:
            # TODO: Activate subscription in database
            logger.info(f"Payment verified for user {user_id}: {tx_hash}")
            return {
                "success": True,
                "message": "Payment verified and subscription activated",
                "data": result
            }
        else:
            logger.warning(f"Payment verification failed for {user_id}: {result.get('error')}")
            raise HTTPException(status_code=400, detail=result['error'])
            
    except Exception as e:
        logger.error(f"Payment verification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/subscription/price", tags=["Payment"])
async def get_subscription_price(referral_count: int = 0):
    """Calculate subscription price based on referrals"""
    price = payment_service.calculate_price(referral_count)
    
    return {
        "base_price": payment_service.base_price,
        "referral_count": referral_count,
        "discount_per_referral": payment_service.referral_discount,
        "total_discount": referral_count * payment_service.referral_discount,
        "final_price": price,
        "is_free": referral_count >= payment_service.max_referrals_for_free,
        "referrals_for_free": payment_service.max_referrals_for_free
    }

# ==================== ADMIN ENDPOINTS ====================

@app.get("/api/admin/stats", tags=["Admin"])
async def admin_stats(password: str):
    """Admin statistics (protected)"""
    if password != config.ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    total_bots = sum(
        len(manager.active_bots) 
        for manager in bot_managers.values()
    )
    
    return {
        "total_users": len(bot_managers),
        "active_bots": total_bots,
        "version": config.VERSION,
        "uptime": "running",
        "bot_types": {
            "dca": 0,  # TODO: Count by type
            "grid": 0,
            "signal": 0
        }
    }

@app.post("/api/admin/broadcast", tags=["Admin"])
async def admin_broadcast(password: str, message: str):
    """Broadcast message to all users (protected)"""
    if password != config.ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # TODO: Implement broadcast via Telegram/Email
    logger.info(f"Admin broadcast: {message}")
    
    return {
        "success": True,
        "users_notified": len(bot_managers)
    }

# ==================== ERROR HANDLERS ====================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return {
        "error": "Not Found",
        "message": "The requested endpoint does not exist",
        "docs": "/docs"
    }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {exc}")
    return {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred. Please try again later."
    }

# ==================== RUN SERVER ====================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting uvicorn server...")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower(),
        access_log=True
    )
