"""
Authentication endpoints for VCaaS API.
Handles user registration, login, profile management, and API key generation.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from datetime import datetime, timedelta

from ...core.config import settings
from ...core.database import get_db
from ...core.security import (
    create_access_token, 
    verify_password, 
    get_password_hash,
    verify_token
)
from ...models.user import User
from ...schemas.auth import (
    UserCreate, 
    UserLogin, 
    UserResponse, 
    Token,
    ApiKeyCreate,
    ApiKeyResponse
)

# Implementation Note: Main.py adds prefix="/api/auth", so no prefix here
router = APIRouter(tags=["authentication"])
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user from JWT token."""
    token = credentials.credentials
    
    # MOCK AUTH KEY
    if settings.DEBUG and token == "mock-token-123":
        user = db.query(User).filter(User.email == "demo@vcaas.com").first()
        if not user:
            # Auto-create mock user if missing
            password_hash = get_password_hash("demo123")
            user = User(
                username="demo_user",
                email="demo@vcaas.com",
                hashed_password=password_hash,
                full_name="Demo User",
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account."""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=True, # Auto verify for simplicity
        is_premium=False,
        subscription_tier="free",
        created_at=user.created_at,
        last_login=user.last_login
    )

@router.post("/login", response_model=Token)
async def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return access token."""
    user = db.query(User).filter(
        (User.email == credentials.email_or_username) | 
        (User.username == credentials.email_or_username)
    ).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile information."""
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_verified=True, 
        is_premium=False,
        subscription_tier="free",
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    profile_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile information."""
    # Update allowed fields
    if "full_name" in profile_data:
        current_user.full_name = profile_data["full_name"]
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_verified=True, 
        is_premium=False,
        subscription_tier="free",
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )

@router.post("/api-keys", response_model=ApiKeyResponse)
async def create_api_key(
    key_data: ApiKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a new API key for the user."""
    # Implementation for API key generation
    
    api_key = f"vcaas_{current_user.id}_{datetime.utcnow().timestamp()}"
    
    return ApiKeyResponse(
        key_id="key_123",
        key=api_key,
        name=key_data.name,
        key_prefix=api_key[:8],
        scopes=key_data.scopes,
        created_at=datetime.utcnow()
    )

@router.post("/verify-token")
async def verify_access_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Verify if the provided token is valid."""
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    return {"valid": True, "user_id": payload.get("sub")}
