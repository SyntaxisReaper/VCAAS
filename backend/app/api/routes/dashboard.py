from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from datetime import datetime

from app.core.database import get_db

router = APIRouter()
security = HTTPBearer()


class DashboardStats(BaseModel):
    total_voices: int
    minutes_generated: int
    active_training: int
    storage_used_gb: float


class UsageLogResponse(BaseModel):
    id: str
    usage_type: str
    status: str
    output_duration: float
    created_at: datetime
    voice_sample_name: str


class ActivityItem(BaseModel):
    id: str
    action: str
    target: str
    timestamp: datetime
    type: str


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard statistics for the current user"""
    # TODO: Verify JWT token and get user
    # TODO: Calculate actual stats from database
    
    # Mock response for now
    return {
        "total_voices": 12,
        "minutes_generated": 1247,
        "active_training": 3,
        "storage_used_gb": 2.4
    }


@router.get("/usage", response_model=List[UsageLogResponse])
async def get_usage_logs(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """Get user's usage logs"""
    # TODO: Verify JWT token and get user
    # TODO: Query usage logs from database
    
    # Mock response for now
    return [
        {
            "id": "usage-1",
            "usage_type": "tts_generation",
            "status": "completed",
            "output_duration": 45.2,
            "created_at": datetime.now(),
            "voice_sample_name": "Professional Voice"
        },
        {
            "id": "usage-2",
            "usage_type": "voice_training",
            "status": "completed",
            "output_duration": 0.0,
            "created_at": datetime.now(),
            "voice_sample_name": "Character Voice"
        }
    ]


@router.get("/activity", response_model=List[ActivityItem])
async def get_recent_activity(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
    limit: int = 20
):
    """Get recent user activity"""
    # TODO: Verify JWT token and get user
    # TODO: Query recent activity from database
    
    # Mock response for now
    return [
        {
            "id": "activity-1",
            "action": "Voice clone generated",
            "target": "Professional Voice",
            "timestamp": datetime.now(),
            "type": "generation"
        },
        {
            "id": "activity-2", 
            "action": "Training completed",
            "target": "Character Voice",
            "timestamp": datetime.now(),
            "type": "training"
        },
        {
            "id": "activity-3",
            "action": "New voice sample uploaded",
            "target": "Casual Narrator",
            "timestamp": datetime.now(),
            "type": "upload"
        }
    ]


@router.get("/analytics")
async def get_analytics(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
    days: int = 30
):
    """Get usage analytics for charts"""
    # TODO: Verify JWT token and get user
    # TODO: Generate analytics data from usage logs
    
    # Mock response for now
    return {
        "daily_usage": [
            {"date": "2024-01-01", "minutes": 45},
            {"date": "2024-01-02", "minutes": 62},
            {"date": "2024-01-03", "minutes": 38}
        ],
        "usage_by_type": [
            {"type": "TTS Generation", "count": 145, "percentage": 65},
            {"type": "Voice Training", "count": 48, "percentage": 22},
            {"type": "Voice Cloning", "count": 29, "percentage": 13}
        ],
        "voice_quality_distribution": [
            {"quality": "Excellent", "count": 8},
            {"quality": "Good", "count": 3},
            {"quality": "Fair", "count": 1}
        ]
    }
