from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy import select, update, delete
import uuid
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.api.routes.auth import get_current_user
from app.models.voice import VoiceSample

router = APIRouter()
security = HTTPBearer()


class VoiceSampleResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    status: str
    duration: float
    quality_score: Optional[float]
    usage_count: int
    created_at: datetime
    is_public: bool
    
    class Config:
        from_attributes = True


class VoiceSampleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    language: str = "en"
    is_public: bool = False


class VoiceSampleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None


@router.get("/samples", response_model=List[VoiceSampleResponse])
async def get_voice_samples(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """Get user's voice samples"""
    result = await db.execute(
        select(VoiceSample)
        .where(VoiceSample.owner_id == user.get("uid"))
        .offset(offset)
        .limit(limit)
    )
    samples = result.scalars().all()
    return samples
    
    # Mock response for now
    return [
        {
            "id": "sample-1",
            "name": "Professional Voice",
            "description": "My professional speaking voice",
            "status": "trained",
            "duration": 154.5,
            "quality_score": 95.2,
            "usage_count": 1247,
            "created_at": datetime.now(),
            "is_public": False
        },
        {
            "id": "sample-2", 
            "name": "Casual Narrator",
            "description": "Relaxed storytelling voice",
            "status": "training",
            "duration": 105.3,
            "quality_score": None,
            "usage_count": 0,
            "created_at": datetime.now(),
            "is_public": True
        }
    ]


@router.post("/samples", response_model=VoiceSampleResponse)
async def create_voice_sample(
    voice_data: VoiceSampleCreate,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new voice sample"""
    sample = VoiceSample(
        id=str(uuid.uuid4()),
        owner_id=user.get("uid"),
        name=voice_data.name,
        description=voice_data.description,
        status="uploaded",
        duration=0.0,
        is_public=voice_data.is_public,
    )
    db.add(sample)
    await db.commit()
    await db.refresh(sample)
    return sample
    
    # Mock response for now
    return {
        "id": "new-sample-id",
        "name": voice_data.name,
        "description": voice_data.description,
        "status": "uploaded",
        "duration": 0.0,
        "quality_score": None,
        "usage_count": 0,
        "created_at": datetime.now(),
        "is_public": voice_data.is_public
    }


@router.post("/samples/{sample_id}/upload")
async def upload_voice_file(
    sample_id: str,
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload audio file for voice sample"""
    # TODO: Validate audio file format
    # TODO: Save file to S3 or local storage
    # TODO: Start processing/training pipeline
    
    return {
        "message": "File uploaded successfully",
        "sample_id": sample_id,
        "filename": file.filename,
        "status": "processing"
    }


@router.get("/samples/{sample_id}", response_model=VoiceSampleResponse)
async def get_voice_sample(
    sample_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific voice sample"""
    result = await db.execute(select(VoiceSample).where(VoiceSample.id == sample_id))
    sample = result.scalar_one_or_none()
    if not sample:
        raise HTTPException(status_code=404, detail="Voice sample not found")
    if sample.owner_id != user.get("uid") and not sample.is_public:
        raise HTTPException(status_code=403, detail="Not authorized to access this sample")
    return sample
    # TODO: Check user permissions
    
    # Mock response for now
    return {
        "id": sample_id,
        "name": "Professional Voice",
        "description": "My professional speaking voice",
        "status": "trained",
        "duration": 154.5,
        "quality_score": 95.2,
        "usage_count": 1247,
        "created_at": datetime.now(),
        "is_public": False
    }


@router.put("/samples/{sample_id}", response_model=VoiceSampleResponse)
async def update_voice_sample(
    sample_id: str,
    voice_data: VoiceSampleUpdate,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update voice sample"""
    result = await db.execute(select(VoiceSample).where(VoiceSample.id == sample_id))
    sample = result.scalar_one_or_none()
    if not sample:
        raise HTTPException(status_code=404, detail="Voice sample not found")
    if sample.owner_id != user.get("uid"):
        raise HTTPException(status_code=403, detail="Not authorized to update this sample")

    if voice_data.name is not None:
        sample.name = voice_data.name
    if voice_data.description is not None:
        sample.description = voice_data.description
    if voice_data.is_public is not None:
        sample.is_public = voice_data.is_public

    await db.commit()
    await db.refresh(sample)
    return sample
    # TODO: Check user permissions
    
    # Mock response for now
    return {
        "id": sample_id,
        "name": voice_data.name or "Updated Voice",
        "description": voice_data.description,
        "status": "trained",
        "duration": 154.5,
        "quality_score": 95.2,
        "usage_count": 1247,
        "created_at": datetime.now(),
        "is_public": voice_data.is_public or False
    }


@router.delete("/samples/{sample_id}")
async def delete_voice_sample(
    sample_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete voice sample"""
    result = await db.execute(select(VoiceSample).where(VoiceSample.id == sample_id))
    sample = result.scalar_one_or_none()
    if not sample:
        raise HTTPException(status_code=404, detail="Voice sample not found")
    if sample.owner_id != user.get("uid"):
        raise HTTPException(status_code=403, detail="Not authorized to delete this sample")

    await db.delete(sample)
    await db.commit()
    return {"message": "Voice sample deleted successfully"}
    # TODO: Delete from database and storage
    
    return {"message": "Voice sample deleted successfully"}


@router.post("/samples/{sample_id}/train")
async def train_voice_sample(
    sample_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start training for voice sample"""
    # TODO: Start background training task for user's sample
    # TODO: Update sample status
    
    return {
        "message": "Training started",
        "sample_id": sample_id,
        "status": "training"
    }
