"""
Enhanced Dashboard API Endpoints (Stubbed for SQL/No-Mongo mode)
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import get_current_active_user
from app.models.user import User

router = APIRouter(tags=["dashboard-enhanced"])

@router.get("/stats")
async def get_dashboard_stats(current_user: User = Depends(get_current_active_user)):
    """Get comprehensive dashboard statistics (Stub)"""
    return {
        "total_samples": 0,
        "samples_suitable_for_training": 0,
        "average_sample_quality": 0.0,
        "total_voice_models": 0,
        "deployed_models": 0,
        "training_models": 0,
        "total_tts_jobs": 0,
        "completed_tts_jobs": 0,
        "total_characters_generated": 0,
        "total_audio_duration": 0.0,
        "credits_remaining": 0,
        "monthly_limits": {},
        "usage_this_month": {},
        "recent_activity": []
    }

@router.get("/activity")
async def get_recent_activity(current_user: User = Depends(get_current_active_user)):
    return []

@router.get("/usage-chart")
async def get_usage_chart(current_user: User = Depends(get_current_active_user)):
    return {"labels": [], "datasets": []}

@router.get("/models")
async def get_user_models(current_user: User = Depends(get_current_active_user)):
    return []

@router.get("/jobs")
async def get_user_jobs(current_user: User = Depends(get_current_active_user)):
    return []

@router.get("/quota-status")
async def get_quota_status(current_user: User = Depends(get_current_active_user)):
    return {
        "subscription_tier": "free",
        "credits_remaining": 0,
        "monthly_limits": {},
        "current_usage": {},
        "usage_percentages": {},
        "reset_date": "2024-01-01"
    }

@router.get("/recommendations")
async def get_recommendations(current_user: User = Depends(get_current_active_user)):
    return {"recommendations": []}