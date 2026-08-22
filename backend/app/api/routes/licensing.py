from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db

router = APIRouter()
security = HTTPBearer()


class LicenseResponse(BaseModel):
    id: str
    license_type: str
    status: str
    title: str
    description: Optional[str]
    voice_sample_name: str
    licensee_name: str
    licensor_name: str
    is_free: bool
    price: Optional[float]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class LicenseCreate(BaseModel):
    voice_sample_id: str
    licensee_id: str
    license_type: str
    title: str
    description: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    is_free: bool = True
    price: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_usage_minutes: Optional[float] = None
    requires_attribution: bool = False


@router.get("/", response_model=List[LicenseResponse])
async def get_licenses(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
    license_type: Optional[str] = None,
    status: Optional[str] = None
):
    """Get user's licenses (both granted and received)"""
    # TODO: Verify JWT token and get user
    # TODO: Query licenses from database
    
    # Mock response for now
    return [
        {
            "id": "license-1",
            "license_type": "personal",
            "status": "active",
            "title": "Personal Use License",
            "description": "For personal projects only",
            "voice_sample_name": "Professional Voice",
            "licensee_name": "John Doe",
            "licensor_name": "Current User",
            "is_free": True,
            "price": None,
            "start_date": datetime.now(),
            "end_date": None,
            "created_at": datetime.now()
        }
    ]


@router.post("/", response_model=LicenseResponse)
async def create_license(
    license_data: LicenseCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Create a new license"""
    # TODO: Verify JWT token and get user
    # TODO: Validate voice sample ownership
    # TODO: Create license in database
    
    # Mock response for now
    return {
        "id": "new-license-id",
        "license_type": license_data.license_type,
        "status": "pending",
        "title": license_data.title,
        "description": license_data.description,
        "voice_sample_name": "Sample Voice",
        "licensee_name": "Licensee User",
        "licensor_name": "Current User",
        "is_free": license_data.is_free,
        "price": license_data.price,
        "start_date": license_data.start_date,
        "end_date": license_data.end_date,
        "created_at": datetime.now()
    }


@router.get("/{license_id}", response_model=LicenseResponse)
async def get_license(
    license_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Get specific license details"""
    # TODO: Verify JWT token and get user
    # TODO: Check user permissions
    # TODO: Get license from database
    
    # Mock response for now
    return {
        "id": license_id,
        "license_type": "personal",
        "status": "active",
        "title": "Personal Use License",
        "description": "For personal projects only",
        "voice_sample_name": "Professional Voice",
        "licensee_name": "John Doe",
        "licensor_name": "Current User",
        "is_free": True,
        "price": None,
        "start_date": datetime.now(),
        "end_date": None,
        "created_at": datetime.now()
    }


@router.put("/{license_id}/approve")
async def approve_license(
    license_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Approve a pending license"""
    # TODO: Verify JWT token and get user
    # TODO: Check if user is licensor
    # TODO: Update license status
    
    return {
        "message": "License approved successfully",
        "license_id": license_id,
        "status": "active"
    }


@router.put("/{license_id}/revoke")
async def revoke_license(
    license_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Revoke an active license"""
    # TODO: Verify JWT token and get user
    # TODO: Check if user is licensor
    # TODO: Update license status
    
    return {
        "message": "License revoked successfully",
        "license_id": license_id,
        "status": "revoked"
    }


@router.delete("/{license_id}")
async def delete_license(
    license_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Delete a license"""
    # TODO: Verify JWT token and get user
    # TODO: Check user permissions
    # TODO: Delete license from database
    
    return {"message": "License deleted successfully"}


@router.get("/voice-samples/{sample_id}/permissions")
async def get_voice_permissions(
    sample_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Get permissions for a specific voice sample"""
    # TODO: Verify JWT token and get user
    # TODO: Check voice sample ownership
    # TODO: Get all licenses for the voice sample
    
    return {
        "voice_sample_id": sample_id,
        "is_public": False,
        "total_licenses": 3,
        "active_licenses": 2,
        "pending_approvals": 1,
        "licenses": [
            {
                "id": "license-1",
                "licensee_name": "John Doe",
                "license_type": "personal",
                "status": "active",
                "created_at": datetime.now()
            }
        ]
    }
