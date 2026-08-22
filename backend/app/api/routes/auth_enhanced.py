"""
Enhanced Authentication API Endpoints (Stubbed for SQL/No-Mongo mode)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from app.core.auth import get_current_active_user, get_current_user
from app.models.user import User

router = APIRouter(tags=["auth-enhanced"])

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict

@router.post("/register", response_model=TokenResponse)
async def register_user():
    raise HTTPException(status_code=501, detail="Registration not implemented in stub")

@router.post("/login", response_model=TokenResponse)
async def login_user(login_data: UserLogin):
    raise HTTPException(status_code=501, detail="Use /api/auth/login instead")

@router.get("/profile")
async def get_user_profile(current_user: User = Depends(get_current_active_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active
    }

@router.put("/profile")
async def update_user_profile(current_user: User = Depends(get_current_active_user)):
    return {"message": "Profile updated successfully"}

@router.get("/stats")
async def get_user_stats(current_user: User = Depends(get_current_active_user)):
    return {
        "total_voice_samples": 0,
        "credits_remaining": 0
    }

@router.post("/change-password")
async def change_password(current_user: User = Depends(get_current_active_user)):
    return {"message": "Password changed successfully"}

@router.post("/generate-api-key")
async def generate_api_key(current_user: User = Depends(get_current_active_user)):
    return {"api_key": "stub-key", "created_at": "2024-01-01", "message": "API key generated"}

@router.delete("/api-key")
async def revoke_api_key(current_user: User = Depends(get_current_active_user)):
    return {"message": "API key revoked"}

@router.post("/logout")
async def logout_user(current_user: User = Depends(get_current_user)):
    return {"message": "Logged out successfully"}

@router.get("/verify-token")
async def verify_token(current_user: User = Depends(get_current_active_user)):
    return {
        "valid": True,
        "user_id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email
    }