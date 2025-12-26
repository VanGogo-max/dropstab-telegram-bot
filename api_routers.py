# api_routes.py - Complete API Routes for CryptoTradeBot Pro
"""
All API endpoints needed for frontend integration.
Add to main.py with: app.include_router(router)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import secrets
import logging

logger = logging.getLogger(__name__)

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWT Configuration
SECRET_KEY = secrets.token_urlsafe(32)  # TODO: Move to config/env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

router = APIRouter()

# ==================== PYDANTIC MODELS ====================

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    referral_code: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]

class APIKeyData(BaseModel):
    exchange: str
    keys: Dict[str, str]

class BotConfigData(BaseModel):
    config: Dict[str, Any]

# ==================== HELPER FUNCTIONS ====================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return {
            "id": user_id,
            "email": payload.get("email"),
            "name": payload.get("name", "User")
        }
    except jwt.PyJWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise credentials_exception

# ==================== AUTHENTICATION ====================

@router.post("/api/auth/register", response_model=Token)
async def register(user: UserRegister):
    """Register new user"""
    try:
        # TODO: Check if email exists in database
        # TODO: Validate referral code if provided
        # TODO: Save to database
        
        user_id = f"user_{secrets.token_hex(8)}"
        hashed_password = get_password_hash(user.password)
        
        logger.info(f"New user registered: {user.email}")
        
        # Create token
        access_token = create_access_token(
            data={
                "sub": user_id,
                "email": user.email,
                "name": user.name
            },
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        # Apply referral bonus if code provided
        referral_bonus = 0
        if user.referral_code:
            # TODO: Validate and apply referral
            referral_bonus = 1
            logger.info(f"Referral code applied: {user.referral_code}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "email": user.email,
                "name": user.name,
                "referralCount": referral_bonus
            }
        }
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/api/auth/login", response_model=Token)
async def login(user: UserLogin):
    """User login"""
    try:
        # TODO: Verify credentials from database
        # For now, mock authentication
        
        user_id = "user_demo123"
        
        logger.info(f"User login: {user.email}")
        
        access_token = create_access_token(
            data={
                "sub": user_id,
                "email": user.email,
                "name": "Demo User"
            },
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "email": user.email,
                "name": "Demo User",
                "referralCount": 3
            }
        }
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

@router.get("/api/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    # TODO: Fetch full user data from database
    return {
        "user": {
            "id": current_user["id"],
            "email": current_user["email"],
            "name": current_user.get("name", "User"),
            "referralCount": 3  # TODO: Get from DB
        }
    }

# ==================== API KEYS MANAGEMENT ====================

@router.get("/api/keys")
async def get_api_keys(current_user: dict = Depends(get_current_user)):
    """Get all API keys (encrypted)"""
    # TODO: Fetch from database, decrypt with user's key
    return {
        "keys": {
            "kcex": {
                "apiKey": "••••••••",
                "apiSecret": "••••••••"
            }
        },
        "validated": {
            "kcex": True,
            "hyperliquid": False,
            "uniswap": False
        }
    }

@router.post("/api/keys")
async def save_api_keys(
    api_key: APIKeyData,
    current_user: dict = Depends(get_current_user)
):
    """Save and validate API keys"""
    try:
        # TODO: Encrypt keys before saving
        # TODO: Validate with actual exchange
        # TODO: Save to database
        
        exchange = api_key.exchange
        keys = api_key.keys
        
        logger.info(f"API keys saved for {exchange} by user {current_user['id']}")
        
        # Mock validation
        import asyncio
        await asyncio.sleep(1)
        
        return {
            "success": True,
            "exchange": exchange,
            "validated": True
        }
    except Exception as e:
        logger.error(f"API key save error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/api/keys/{exchange}")
async def delete_api_keys(
    exchange: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete API keys"""
    try:
        # TODO: Delete from database
        logger.info(f"API keys deleted for {exchange} by user {current_user['id']}")
        return {"success": True, "exchange": exchange}
    except Exception as e:
        logger.error(f"API key delete error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# ==================== BOT CONFIGURATION ====================

@router.get("/api/bots/{bot_id}/config")
async def get_bot_config(
    bot_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get bot configuration"""
    # TODO: Fetch from database
    return {
        "config": {
            "symbol": "BTC/USDT",
            "amount": 100,
            "interval": 24
        }
    }

@router.post("/api/bots/{bot_id}/config")
async def save_bot_config(
    bot_id: str,
    bot_config: BotConfigData,
    current_user: dict = Depends(get_current_user)
):
    """Save bot configuration"""
    try:
        # TODO: Validate config
        # TODO: Save to database
        logger.info(f"Bot config saved: {bot_id} by user {current_user['id']}")
        return {
            "success": True,
            "bot_id": bot_id,
            "config": bot_config.config
        }
    except Exception as e:
        logger.error(f"Bot config save error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# ==================== BOT CONTROLS ====================

@router.get("/api/bots/{bot_id}/status")
async def get_bot_status(
    bot_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get bot status and metrics"""
    # TODO: Get real status from bot_manager
    return {
        "status": "running",
        "metrics": {
            "pnl": 125.50,
            "pnlPercent": 12.55,
            "totalTrades": 47,
            "winRate": 65.5,
            "avgTradeTime": 45,
            "uptime": 86400,
            "lastTrade": datetime.utcnow().isoformat()
        }
    }

@router.post("/api/bots/{bot_id}/start")
async def start_bot(
    bot_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Start bot"""
    try:
        # TODO: Start via bot_manager
        logger.info(f"Bot started: {bot_id} by user {current_user['id']}")
        return {"success": True, "status": "running", "bot_id": bot_id}
    except Exception as e:
        logger.error(f"Bot start error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/api/bots/{bot_id}/pause")
async def pause_bot(
    bot_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Pause bot"""
    try:
        # TODO: Pause via bot_manager
        logger.info(f"Bot paused: {bot_id} by user {current_user['id']}")
        return {"success": True, "status": "paused", "bot_id": bot_id}
    except Exception as e:
        logger.error(f"Bot pause error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/api/bots/{bot_id}/stop")
async def stop_bot(
    bot_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Stop bot"""
    try:
        # TODO: Stop via bot_manager
        logger.info(f"Bot stopped: {bot_id} by user {current_user['id']}")
        return {"success": True, "status": "stopped", "bot_id": bot_id}
    except Exception as e:
        logger.error(f"Bot stop error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# ==================== REFERRALS ====================

@router.get("/api/referrals")
async def get_referrals(current_user: dict = Depends(get_current_user)):
    """Get referral data"""
    # TODO: Fetch from database
    referral_code = "CRYPTO" + current_user["id"][-6:].upper()
    
    return {
        "referralCode": referral_code,
        "stats": {
            "totalReferrals": 5,
            "activeReferrals": 3,
            "totalEarnings": 5.0,
            "pendingEarnings": 0.0,
            "thisMonth": 2.0,
            "isUnlocked": False
        },
        "recentReferrals": [
            {
                "username": "user_abc",
                "status": "active",
                "joinedAt": (datetime.utcnow() - timedelta(days=5)).isoformat(),
                "earned": 1.0
            }
        ]
    }

# ==================== TRADE HISTORY ====================

@router.get("/api/trades")
async def get_trades(
    page: int = 1,
    limit: int = 20,
    sortBy: str = "date",
    sortOrder: str = "desc",
    botId: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get trade history with pagination"""
    # TODO: Fetch from database with filters
    
    trades = []
    for i in range(min(limit, 10)):
        trades.append({
            "id": f"trade_{i+1}",
            "timestamp": (datetime.utcnow() - timedelta(hours=i*2)).isoformat(),
            "botName": "Grid Trading",
            "symbol": "BTC/USDT",
            "type": "buy" if i % 2 == 0 else "sell",
            "amount": 0.001 + (i * 0.0001),
            "price": 45000 + (i * 100),
            "fee": 0.45,
            "pnl": 12.5 if i % 3 == 0 else -5.2 if i % 3 == 1 else None
        })
    
    return {
        "trades": trades,
        "total": 234
    }

# ==================== DASHBOARD ====================

@router.get("/api/dashboard/stats")
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    """Get dashboard statistics"""
    # TODO: Calculate from database
    return {
        "totalPnL": 1250.50,
        "totalPnLPercent": 12.5,
        "activeBots": 3,
        "totalTrades": 156,
        "winRate": 65.5,
        "todayPnL": 45.20,
        "weeklyPnL": 180.30,
        "monthlyPnL": 650.00
    }

@router.get("/api/dashboard/chart")
async def get_dashboard_chart(
    period: str = "7d",
    current_user: dict = Depends(get_current_user)
):
    """Get chart data"""
    # TODO: Fetch from database
    data = []
    for i in range(7):
        date = datetime.utcnow() - timedelta(days=6-i)
        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "pnl": 50 + (i * 20),
            "trades": 10 + i
        })
    
    return {"data": data}

# ==================== NOTIFICATIONS ====================

@router.get("/api/notifications")
async def get_notifications(current_user: dict = Depends(get_current_user)):
    """Get notifications"""
    # TODO: Fetch from database
    return {
        "notifications": [
            {
                "id": "notif_1",
                "type": "success",
                "message": "Grid Trading bot executed profitable trade",
                "timestamp": datetime.utcnow().isoformat(),
                "read": False
            }
        ],
        "unreadCount": 3
    }

@router.post("/api/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Mark notification as read"""
    # TODO: Update in database
    return {"success": True}

# Export
__all__ = ['router']
