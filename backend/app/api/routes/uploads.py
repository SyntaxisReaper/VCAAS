"""
File Upload API Endpoints

Handles voice sample uploads, processing, and management.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from pydantic import BaseModel

from app.api.routes.auth import get_current_user
from app.models.user import User
from app.models.voice import VoiceSample
from app.services.file_upload_service import file_upload_service

router = APIRouter()


class VoiceSampleResponse(BaseModel):
    id: str
    filename: str
    duration_seconds: float
    quality_score: float
    is_suitable_for_training: bool
    transcription: str
    language_detected: str
    created_at: str


class UploadResponse(BaseModel):
    success: bool
    message: str
    voice_sample_id: Optional[str] = None
    file_info: Optional[dict] = None
    quality_analysis: Optional[dict] = None


class UploadStatsResponse(BaseModel):
    total_samples: int
    suitable_for_training: int
    total_duration_minutes: float
    average_quality_score: float
    total_storage_mb: float
    limits: dict


@router.post("/voice-sample", response_model=UploadResponse)
async def upload_voice_sample(
    file: UploadFile = File(...),
    transcription: Optional[str] = Form(None),
    language: Optional[str] = Form("en"),
    current_user: User = Depends(get_current_user)
):
    """Upload a new voice sample"""
    try:
        result = await file_upload_service.upload_voice_sample(
            file=file,
            user_id=str(current_user.id),
            transcription=transcription,
            language=language
        )
        
        if not result["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return UploadResponse(
            success=True,
            message=result["message"],
            voice_sample_id=result["voice_sample_id"],
            file_info=result["file_info"],
            quality_analysis=result["quality_analysis"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/voice-samples", response_model=List[VoiceSampleResponse])
async def list_voice_samples(
    status_filter: Optional[str] = None,
    training_suitable_only: bool = False,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """List user's voice samples"""
    try:
        # Build query
        query = {"user_id": str(current_user.id)}
        
        if status_filter:
            query["status"] = status_filter
        
        if training_suitable_only:
            query["is_suitable_for_training"] = True
        
        # Get samples
        samples = await VoiceSample.find(query).sort("-created_at").limit(limit).to_list()
        
        # Format response
        result = []
        for sample in samples:
            result.append(VoiceSampleResponse(
                id=str(sample.id),
                filename=sample.filename,
                duration_seconds=sample.duration_seconds or 0,
                quality_score=sample.quality_score or 0,
                is_suitable_for_training=sample.is_suitable_for_training,
                transcription=sample.transcription or "",
                language_detected=sample.language_detected or "en",
                created_at=sample.created_at.isoformat()
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve voice samples"
        )


@router.get("/voice-sample/{sample_id}")
async def get_voice_sample(
    sample_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get details of a specific voice sample"""
    try:
        sample = await VoiceSample.get(sample_id)
        
        if not sample:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Voice sample not found"
            )
        
        # Check ownership
        if sample.user_id != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this voice sample"
            )
        
        return {
            "id": str(sample.id),
            "filename": sample.filename,
            "duration_seconds": sample.duration_seconds,
            "file_size_bytes": sample.file_size_bytes,
            "sample_rate": sample.sample_rate,
            "channels": sample.channels,
            "format": sample.format,
            "quality_score": sample.quality_score,
            "is_suitable_for_training": sample.is_suitable_for_training,
            "transcription": sample.transcription,
            "language_detected": sample.language_detected,
            "status": sample.status,
            "processing_metadata": sample.processing_metadata,
            "quality_analysis": sample.quality_analysis,
            "created_at": sample.created_at.isoformat(),
            "updated_at": sample.updated_at.isoformat() if sample.updated_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve voice sample"
        )


@router.delete("/voice-sample/{sample_id}")
async def delete_voice_sample(
    sample_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a voice sample"""
    try:
        success = await file_upload_service.delete_voice_sample(
            sample_id=sample_id,
            user_id=str(current_user.id)
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Voice sample not found or cannot be deleted"
            )
        
        return {"message": "Voice sample deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete voice sample"
        )


@router.put("/voice-sample/{sample_id}")
async def update_voice_sample(
    sample_id: str,
    transcription: Optional[str] = None,
    language: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Update voice sample metadata"""
    try:
        sample = await VoiceSample.get(sample_id)
        
        if not sample:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Voice sample not found"
            )
        
        # Check ownership
        if sample.user_id != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this voice sample"
            )
        
        # Update fields
        update_data = {}
        if transcription is not None:
            update_data["transcription"] = transcription
        if language is not None:
            update_data["language_detected"] = language
        
        if update_data:
            await sample.update({"$set": update_data})
        
        return {"message": "Voice sample updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update voice sample"
        )


@router.get("/stats", response_model=UploadStatsResponse)
async def get_upload_stats(
    current_user: User = Depends(get_current_user)
):
    """Get upload statistics for the user"""
    try:
        stats = await file_upload_service.get_upload_stats(str(current_user.id))
        
        if "error" in stats:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=stats["error"]
            )
        
        return UploadStatsResponse(**stats)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get upload statistics"
        )


@router.post("/validate")
async def validate_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Validate a file before upload without processing it"""
    try:
        validation = file_upload_service.validate_file(file)
        
        return {
            "valid": validation["valid"],
            "error": validation.get("error"),
            "file_info": {
                "filename": file.filename,
                "content_type": file.content_type,
                "size": getattr(file, 'size', None)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File validation failed"
        )


@router.post("/batch-upload")
async def batch_upload_samples(
    files: List[UploadFile] = File(...),
    transcriptions: Optional[List[str]] = Form(None),
    languages: Optional[List[str]] = Form(None),
    current_user: User = Depends(get_current_user)
):
    """Upload multiple voice samples at once"""
    try:
        if len(files) > 10:  # Limit batch uploads
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 files per batch upload"
            )
        
        results = []
        
        for i, file in enumerate(files):
            try:
                transcription = transcriptions[i] if transcriptions and i < len(transcriptions) else None
                language = languages[i] if languages and i < len(languages) else "en"
                
                result = await file_upload_service.upload_voice_sample(
                    file=file,
                    user_id=str(current_user.id),
                    transcription=transcription,
                    language=language
                )
                
                results.append({
                    "filename": file.filename,
                    "success": result["valid"],
                    "voice_sample_id": result.get("voice_sample_id"),
                    "error": result.get("error")
                })
                
            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": str(e)
                })
        
        successful_uploads = len([r for r in results if r["success"]])
        
        return {
            "total_files": len(files),
            "successful_uploads": successful_uploads,
            "failed_uploads": len(files) - successful_uploads,
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Batch upload failed"
        )