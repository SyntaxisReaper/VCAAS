"""
Security Report API Routes

Handles security report submission and management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.firebase_auth import get_current_user
from pydantic import BaseModel, EmailStr, validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
import uuid
from datetime import datetime

from app.core.database import get_db
from app.models.security_report import SecurityReport, ReportType, ReportSeverity
from loguru import logger


router = APIRouter()
security = HTTPBearer(auto_error=False)


class SecurityReportCreate(BaseModel):
    """Request model for creating security reports"""
    type: ReportType
    severity: ReportSeverity
    description: str
    email: Optional[EmailStr] = None
    anonymous: bool = False
    
    @validator('description')
    def description_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Description cannot be empty')
        if len(v.strip()) < 10:
            raise ValueError('Description must be at least 10 characters long')
        return v.strip()
    
    @validator('email')
    def email_required_if_not_anonymous(cls, v, values):
        if not values.get('anonymous', False) and not v:
            raise ValueError('Email is required when not submitting anonymously')
        return v


class SecurityReportResponse(BaseModel):
    """Response model for security report operations"""
    id: str
    message: str
    status: str
    created_at: datetime


class SecurityReportListResponse(BaseModel):
    """Response model for listing security reports"""
    reports: List[dict]
    total: int
    page: int
    limit: int


@router.post("/report", response_model=SecurityReportResponse)
async def submit_security_report(
    report_data: SecurityReportCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    Submit a new security report
    
    This endpoint allows users to submit security vulnerabilities,
    fraudulent activity reports, and other security concerns.
    """
    try:
        # Generate unique ID for the report
        report_id = str(uuid.uuid4())
        
        # Extract request information for logging
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent", "")
        
        # TODO: Extract user_id from JWT token if authenticated
        user_id = None
        if credentials:
            # For now, we'll skip JWT validation
            # In a real implementation, you would validate the JWT here
            pass
        
        # Create the security report
        security_report = SecurityReport(
            id=report_id,
            report_type=report_data.type,
            severity=report_data.severity,
            description=report_data.description,
            contact_email=report_data.email if not report_data.anonymous else None,
            is_anonymous=report_data.anonymous,
            user_id=user_id,
            ip_address=client_ip,
            user_agent=user_agent,
            status="submitted"
        )
        
        # Save to database
        db.add(security_report)
        await db.commit()
        await db.refresh(security_report)
        
        logger.info(
            f"Security report submitted: {report_id} - "
            f"Type: {report_data.type.value}, Severity: {report_data.severity.value}, "
            f"Anonymous: {report_data.anonymous}, IP: {client_ip}"
        )
        
        return SecurityReportResponse(
            id=report_id,
            message="Security report submitted successfully. Thank you for helping us improve security.",
            status="submitted",
            created_at=security_report.created_at
        )
        
    except Exception as e:
        logger.error(f"Error submitting security report: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to submit security report. Please try again or contact support directly."
        )


@router.get("/reports", response_model=SecurityReportListResponse)
async def list_security_reports(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
    page: int = 1,
    limit: int = 50,
    status: Optional[str] = None,
    severity: Optional[ReportSeverity] = None
):
    """
    List security reports (Admin only)
    
    This endpoint is for administrative purposes to view and manage
    submitted security reports.
    """
    # Enforce admin access
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    # In a real implementation, you would:
    # 1. Validate JWT token
    # 2. Check if user has admin privileges
    # 3. Filter reports based on parameters
    
    try:
        # Build query
        query = select(SecurityReport)
        
        if status:
            query = query.where(SecurityReport.status == status)
        if severity:
            query = query.where(SecurityReport.severity == severity)
        
        # Add pagination
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        reports = result.scalars().all()
        
        # Convert to dict format (excluding sensitive info for non-admin users)
        reports_data = [report.to_dict() for report in reports]
        
        # Get total count
        count_query = select(SecurityReport)
        if status:
            count_query = count_query.where(SecurityReport.status == status)
        if severity:
            count_query = count_query.where(SecurityReport.severity == severity)
            
        total_result = await db.execute(count_query)
        total = len(total_result.scalars().all())
        
        return SecurityReportListResponse(
            reports=reports_data,
            total=total,
            page=page,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Error listing security reports: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve security reports"
        )


@router.get("/report/{report_id}")
async def get_security_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Get a specific security report by ID (Admin only)
    """
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    try:
        query = select(SecurityReport).where(SecurityReport.id == report_id)
        result = await db.execute(query)
        report = result.scalar_one_or_none()
        
        if not report:
            raise HTTPException(status_code=404, detail="Security report not found")
        
        return report.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving security report {report_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve security report"
        )


@router.patch("/report/{report_id}/status")
async def update_report_status(
    report_id: str,
    status: str,
    resolution_notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Update the status of a security report (Admin only)
    """
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    valid_statuses = ["submitted", "reviewing", "resolved", "dismissed"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    try:
        query = select(SecurityReport).where(SecurityReport.id == report_id)
        result = await db.execute(query)
        report = result.scalar_one_or_none()
        
        if not report:
            raise HTTPException(status_code=404, detail="Security report not found")
        
        # Update report
        report.status = status
        if resolution_notes:
            report.resolution_notes = resolution_notes
        if status in ["resolved", "dismissed"]:
            report.resolved_at = datetime.utcnow()
        
        await db.commit()
        
        logger.info(f"Security report {report_id} status updated to {status}")
        
        return {"message": f"Report status updated to {status}", "status": status}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating security report {report_id}: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to update security report status"
        )