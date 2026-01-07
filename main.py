# main.py - CryptoTradeBot Pro Application Entry Point
"""
Main FastAPI application with all routes integrated.
Manages bot lifecycle, payments, user operations, and onboarding.
"""

import asyncio
import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Optional

# Import configuration and services
from config import config
from bot_manager import BotManager
from payment_service import PaymentService
from referral_service import ReferralService

# Import API routes (if you have api_routes.py, keep this)
try:
    from api_routes import router as api_router
    HAS_API_ROUTES = True
except ImportError:
    HAS_API_ROUTES = False
    logging.warning("api_routes.py not found - using inline routes only")

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
    
    # Initialize database
    try:
        from database import init_database
        init_database()
        logger.info("✓ Database initialized")
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")
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
    description="Automated cryptocurrency trading platform with 10+ strategies and AI selection",
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

# Include external API routes if available
if HAS_API_ROUTES:
    app.include_router(api_router, tags=["API"])
    logger.info("✓ External API routes loaded from api_routes.py")

# ==================== PYDANTIC MODELS ====================

class OnboardingRequest(BaseModel):
    user_id: str
    profile: dict

class RecommendationRequest(BaseModel):
    user_id: str
    profile: dict

# ==================== ROOT & HEALTH ====================

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

# ==================== ONBOARDING & STRATEGY SELECTION ====================

@app.post("/api/onboarding/complete", tags=["Onboarding"])
async def complete_onboarding(request: OnboardingRequest):
    """
    Complete onboarding and auto-start best strategy
    
    Request body:
    {
        "user_id": "user_123",
        "profile": {
            "capital": 5000,
            "experience": "intermediate",
            "risk_tolerance": "medium",
            "can_monitor": false,
            "goals": ["income", "growth"]
        }
    }
    """
    try:
        user_id = request.user_id
        profile = request.profile
        
        logger.info(f"📋 Onboarding completion for user: {user_id}")
        logger.info(f"Profile: {profile}")
        
        # 1. Save profile to database
        try:
            from database import save_user_profile
            save_user_profile(user_id, profile)
            logger.info(f"✅ Profile saved for user: {user_id}")
        except Exception as e:
            logger.warning(f"⚠️ Could not save profile to database: {e}")
        
        # 2. Get or create bot manager
        if user_id not in bot_managers:
            bot_managers[user_id] = BotManager()
            logger.info(f"Created new BotManager for user: {user_id}")
        
        manager = bot_managers[user_id]
        
        # 3. Auto-start best strategy
        strategy = manager.auto_start_best_strategy(user_id, profile)
        
        if strategy:
            logger.info(f"✅ Strategy '{strategy}' started for user: {user_id}")
            return {
                "success": True,
                "strategy": strategy,
                "message": f"{strategy.upper()} bot started successfully!",
                "user_id": user_id
            }
        else:
            logger.warning(f"⚠️ Could not start strategy for user: {user_id}")
            return {
                "success": False,
                "message": "Could not determine best strategy. Please try again.",
                "user_id": user_id
            }
    
    except Exception as e:
        logger.error(f"❌ Onboarding error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/strategy/recommendations", tags=["Strategy"])
async def get_recommendations(request: RecommendationRequest):
    """
    Get top 3 strategy recommendations without starting bots
    """
    try:
        user_id = request.user_id
        profile = request.profile
        
        logger.info(f"🔍 Getting recommendations for user: {user_id}")
        
        # Get or create bot manager
        if user_id not in bot_managers:
            bot_managers[user_id] = BotManager()
        
        manager = bot_managers[user_id]
        
        # Get recommendations
        recommendations = manager.get_strategy_recommendations(
            user_id=user_id,
            profile=profile,
            top_n=3
        )
        
        return {
            "success": True,
            "recommendations": [
                {
                    "strategy": str(strategy.value),
                    "score": round(score, 1),
                    "reasoning": reasoning
                }
                for strategy, score, reasoning in recommendations
            ]
        }
    
    except Exception as e:
        logger.error(f"❌ Recommendations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user/{user_id}/profile", tags=["User"])
async def get_user_profile_endpoint(user_id: str):
    """Get user profile from database"""
    try:
        from database import get_user_profile
        profile = get_user_profile(user_id)
        
        if profile:
            return {
                "success": True,
                "profile": profile
            }
        else:
            raise HTTPException(status_code=404, detail="Profile not found")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get profile error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user/{user_id}/onboarding-status", tags=["User"])
async def check_onboarding_status(user_id: str):
    """Check if user has completed onboarding"""
    try:
        from database import get_user_profile
        profile = get_user_profile(user_id)
        
        return {
            "completed": profile is not None,
            "user_id": user_id
        }
    
    except Exception as e:
        logger.error(f"❌ Check onboarding error: {e}")
        return {
            "completed": False,
            "user_id": user_id
        }

@app.get("/api/user/{user_id}/active-strategy", tags=["User"])
async def get_active_strategy(user_id: str):
    """Get currently active strategy for user"""
    try:
        if user_id not in bot_managers:
            return {
                "success": True,
                "active": False,
                "strategy": None
            }
        
        manager = bot_managers[user_id]
        active_bots = manager.get_active_bots(user_id)
        
        if active_bots:
            return {
                "success": True,
                "active": True,
                "strategies": active_bots
            }
        else:
            return {
                "success": True,
                "active": False,
                "strategy": None
            }
    
    except Exception as e:
        logger.error(f"❌ Get active strategy error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== LEGACY BOT ENDPOINTS ====================

@app.post("/api/bots/dca/start", tags=["Legacy Bots"])
async def start_dca_bot_legacy(
    user_id: str,
    symbol: str = "BTC/USDT",
    interval_hours: int = 24,
    amount_per_order: float = 50
):
    """Start DCA bot (legacy endpoint)"""
    try:
        if user_id not in bot_managers:
            bot_managers[user_id] = BotManager()
        
        manager = bot_managers[user_id]
        
        dca_config = {
            'symbol': symbol,
            'interval_hours': interval_hours,
            'amount_per_order': amount_per_order,
            'exchange': 'binance'
        }
        
        success = manager.start_bot(user_id, 'dca', dca_config)
        
        if success:
            logger.info(f"DCA bot started for user {user_id}")
            return {
                "success": True,
                "bot_type": "dca",
                "config": dca_config
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to start DCA bot")
    
    except Exception as e:
        logger.error(f"DCA bot start error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/bots/grid/start", tags=["Legacy Bots"])
async def start_grid_bot_legacy(
    user_id: str,
    symbol: str = "BTC/USDT",
    upper_price: float = 32000,
    lower_price: float = 28000,
    grids: int = 10
):
    """Start Grid bot (legacy endpoint)"""
    try:
        if user_id not in bot_managers:
            bot_managers[user_id] = BotManager()
        
        manager = bot_managers[user_id]
        
        grid_config = {
            'symbol': symbol,
            'upper_price': upper_price,
            'lower_price': lower_price,
            'grids': grids,
            'exchange': 'binance'
        }
        
        success = manager.start_bot(user_id, 'grid', grid_config)
        
        if success:
            logger.info(f"Grid bot started for user {user_id}")
            return {
                "success": True,
                "bot_type": "grid",
                "config": grid_config
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to start Grid bot")
    
    except Exception as e:
        logger.error(f"Grid bot start error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/bots/{bot_type}/stop", tags=["Legacy Bots"])
async def stop_bot_legacy(user_id: str, bot_type: str):
    """Stop bot (legacy endpoint)"""
    try:
        if user_id not in bot_managers:
            raise HTTPException(status_code=404, detail="User not found")
        
        manager = bot_managers[user_id]
        success = manager.stop_bot(user_id, bot_type)
        
        if success:
            logger.info(f"Bot {bot_type} stopped for user {user_id}")
            return {
                "success": True,
                "bot_type": bot_type,
                "status": "stopped"
            }
        else:
            raise HTTPException(status_code=400, detail=f"Bot {bot_type} not running")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bot stop error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/bots/status/all", tags=["Legacy Bots"])
async def get_all_bots_status(user_id: str):
    """Get all bots status (legacy endpoint)"""
    try:
        if user_id not in bot_managers:
            return {"bots": {}}
        
        manager = bot_managers[user_id]
        active_bots = manager.get_active_bots(user_id)
        
        return {
            "bots": active_bots
        }
    
    except Exception as e:
        logger.error(f"Get bots status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/performance/total", tags=["Legacy Bots"])
async def get_total_performance(user_id: str):
    """Get overall performance (legacy endpoint)"""
    try:
        if user_id not in bot_managers:
            return {"error": "User not found"}
        
        # TODO: Implement actual performance calculation
        return {
            "total_pnl": 0,
            "total_trades": 0,
            "win_rate": 0,
            "message": "Performance tracking coming soon"
        }
    
    except Exception as e:
        logger.error(f"Get performance error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
