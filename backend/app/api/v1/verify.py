"""
Watermark verification endpoints for VCaaS API v1.
Handles watermark detection, verification, and forensic analysis.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import tempfile
import os
from datetime import datetime
import uuid

from ...core.database import get_db
from ...core.watermark import WatermarkService
from ...services.forensics_service import ForensicsService
from ...services.speaker_verification import SpeakerVerifier
from ...services.antispoof import AntiSpoofDetector
from ...services.audio_analysis import AudioAnalysisService
from ...models.user import User
from ...models.watermark import WatermarkVerification
from .auth import get_current_user
from ...schemas.watermark import (
    WatermarkVerificationResponse,
    ForensicAnalysisResponse
)
from fastapi.encoders import jsonable_encoder
import numpy as np

# MOCK USER FOR TESTING
def mock_get_current_user():
    from ...models.user import User
    return User(id="test_user", is_premium=True)

router = APIRouter(prefix="/verify", tags=["watermark-verification"])

@router.post("/watermark", response_model=WatermarkVerificationResponse)
async def verify_watermark(
    file: UploadFile = File(...),
    method: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify watermark in uploaded audio file.
    
    Args:
        file: Audio file to analyze
        method: Detection method ('mvp', 'robust', or None for auto-detect)
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Watermark verification results
    """
    
    # Validate file type
    allowed_types = ['audio/wav', 'audio/mp3', 'audio/flac', 'audio/m4a']
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_types)}"
        )
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        # Initialize watermark service
        watermark_service = WatermarkService()
        
        # Detect watermark
        detection_result = await watermark_service.detect_watermark(
            audio_path=temp_file_path,
            method=method
        )
        
        # Generate verification ID
        verification_id = f"verify_{uuid.uuid4().hex[:12]}"
        
        # Store verification record
        verification = WatermarkVerification(
            id=verification_id,
            user_id=current_user.id,
            original_filename=file.filename,
            detection_method=detection_result.get('detection_method', 'unknown'),
            watermark_found=detection_result.get('found', False),
            watermark_id=detection_result.get('watermark_id'),
            license_id=detection_result.get('license_id'),
            confidence_score=detection_result.get('confidence', 0.0),
            detection_metadata=detection_result,
            verified_at=datetime.utcnow()
        )
        
        db.add(verification)
        db.commit()
        db.refresh(verification)
        
        # Prepare response
        response_data = WatermarkVerificationResponse(
            verification_id=verification_id,
            watermark_found=detection_result.get('found', False),
            watermark_id=detection_result.get('watermark_id'),
            license_id=detection_result.get('license_id'),
            confidence_score=detection_result.get('confidence', 0.0),
            detection_method=detection_result.get('detection_method', 'unknown'),
            timestamp=detection_result.get('timestamp'),
            signature_valid=detection_result.get('signature_valid', False),
            verification_time=verification.verified_at,
            metadata=detection_result
        )
        
        return response_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Watermark verification failed: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

@router.post("/forensics")
async def forensic_analysis(
    file: UploadFile = File(...),
    analysis_depth: str = "standard",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Perform comprehensive forensic analysis on audio file.
    
    Args:
        file: Audio file to analyze
        analysis_depth: Analysis depth ('quick', 'standard', 'deep')
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Comprehensive forensic analysis results
    """
    
    # Check user permissions for forensic analysis
    if not current_user.is_premium:  # Assuming premium feature
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forensic analysis requires premium subscription"
        )
    
    # Validate file
    if file.size > 100 * 1024 * 1024:  # 100MB limit
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large for forensic analysis"
        )
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        # Initialize services
        watermark_service = WatermarkService()
        forensics_service = ForensicsService()
        
        # Perform watermark detection
        watermark_results = await watermark_service.detect_watermark(
            audio_path=temp_file_path,
            method=None  # Auto-detect both methods
        )
        
        # Perform forensic analysis
        forensic_results = await forensics_service.analyze_audio(
            audio_path=temp_file_path,
            depth=analysis_depth
        )
        
        # DEBUG LOGGING
        with open("debug_output.txt", "w") as f:
            f.write(f"watermark_results: {watermark_results}\n")
            f.write(f"forensic_results: {forensic_results}\n")
            f.write("TYPES:\n")
            for k, v in forensic_results.items():
                f.write(f"Key: {k}, Type: {type(v)}, Value: {v}\n")
                if isinstance(v, dict):
                    for k2, v2 in v.items():
                        f.write(f"  SubKey: {k2}, Type: {type(v2)}, Value: {v2}\n")
        
        # Generate analysis ID
        analysis_id = f"forensic_{uuid.uuid4().hex[:12]}"
        
        # Combine results
        combined_results = {
            'analysis_id': analysis_id,
            'watermark_analysis': watermark_results,
            'forensic_analysis': forensic_results,
            'analysis_depth': analysis_depth,
            'analyzed_at': datetime.utcnow(),
            'file_metadata': {
                'filename': file.filename,
                'size_bytes': file.size,
                'content_type': file.content_type
            }
        }
        
        # Store analysis record
        # This would typically be saved to a ForensicAnalysis model
        
        response = ForensicAnalysisResponse(
            analysis_id=analysis_id,
            watermark_found=watermark_results.get('found', False),
            watermark_details=watermark_results,
            audio_integrity=forensic_results.get('integrity', {}),
            manipulation_detected=forensic_results.get('manipulation_detected', False),
            manipulation_details=forensic_results.get('manipulation_details', []),
            metadata_analysis=forensic_results.get('metadata', {}),
            spectral_analysis=forensic_results.get('spectral', {}),
            confidence_score=min(
                watermark_results.get('confidence', 0.0),
                forensic_results.get('confidence', 0.0)
            ),
            analysis_depth=analysis_depth,
            analyzed_at=combined_results['analyzed_at'],
            recommendations=forensic_results.get('recommendations', [])
        )
        # Helper for manual sanitization
        def sanitize_numpy(obj):
            if isinstance(obj, dict):
                return {k: sanitize_numpy(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [sanitize_numpy(v) for v in obj]
            elif isinstance(obj, tuple):
                return tuple(sanitize_numpy(v) for v in obj)
            elif hasattr(obj, 'item') and not isinstance(obj, (dict, list, tuple)):
                return obj.item()
            elif isinstance(obj, np.ndarray):
                return sanitize_numpy(obj.tolist())
            return obj

        sanitized_response = sanitize_numpy(response.model_dump())
        return jsonable_encoder(sanitized_response)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Forensic analysis failed: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

@router.post("/speaker-match")
async def speaker_match(
    reference: UploadFile = File(...),
    sample: UploadFile = File(...),
):
    """Compare two voices and return similarity/decision."""
    import tempfile, os
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(reference.filename)[1]) as f1:
            ref_path = f1.name; f1.write(await reference.read())
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(sample.filename)[1]) as f2:
            qry_path = f2.name; f2.write(await sample.read())
        verifier = SpeakerVerifier()
        result = verifier.verify(ref_path, qry_path)
        return result
    finally:
        for p in [locals().get('ref_path'), locals().get('qry_path')]:
            try:
                if p and os.path.exists(p): os.unlink(p)
            except Exception: pass


@router.post("/antispoof")
async def antispoof_check(file: UploadFile = File(...)):
    """Estimate deepfake likelihood for a single audio file."""
    import tempfile, os
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as f:
            path = f.name; f.write(await file.read())
        det = AntiSpoofDetector()
        res = det.detect(path)
        return res
    finally:
        try:
            if 'path' in locals() and os.path.exists(path): os.unlink(path)
        except Exception: pass


@router.post("/spectral-graphs")
async def spectral_graphs(file: UploadFile = File(...)):
    """Return spectral features for plotting (mel, mfcc, centroid, etc.)."""
    import tempfile, os
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as f:
            path = f.name; f.write(await file.read())
        svc = AudioAnalysisService()
        return svc.analyze(path)
    finally:
        try:
            if 'path' in locals() and os.path.exists(path): os.unlink(path)
        except Exception: pass


@router.get("/history")
async def get_verification_history(
    limit: int = 20,
    watermark_found: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get verification history for the current user."""
    
    query = db.query(WatermarkVerification).filter(
        WatermarkVerification.user_id == current_user.id
    )
    
    if watermark_found is not None:
        query = query.filter(WatermarkVerification.watermark_found == watermark_found)
    
    verifications = query.order_by(
        WatermarkVerification.verified_at.desc()
    ).limit(min(limit, 100)).all()
    
    return [
        {
            "verification_id": verification.id,
            "original_filename": verification.original_filename,
            "watermark_found": verification.watermark_found,
            "watermark_id": verification.watermark_id,
            "license_id": verification.license_id,
            "confidence_score": verification.confidence_score,
            "detection_method": verification.detection_method,
            "verified_at": verification.verified_at
        }
        for verification in verifications
    ]

@router.get("/{verification_id}")
async def get_verification_details(
    verification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed results of a specific verification."""
    
    verification = db.query(WatermarkVerification).filter(
        WatermarkVerification.id == verification_id,
        WatermarkVerification.user_id == current_user.id
    ).first()
    
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verification not found"
        )
    
    return {
        "verification_id": verification.id,
        "original_filename": verification.original_filename,
        "watermark_found": verification.watermark_found,
        "watermark_id": verification.watermark_id,
        "license_id": verification.license_id,
        "confidence_score": verification.confidence_score,
        "detection_method": verification.detection_method,
        "detection_metadata": verification.detection_metadata,
        "verified_at": verification.verified_at
    }

@router.post("/batch-verify")
async def batch_verify_watermarks(
    files: list[UploadFile],
    method: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify watermarks in multiple audio files."""
    
    if len(files) > 10:  # Limit batch size
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 files per batch"
        )
    
    results = []
    
    for file in files:
        try:
            # Validate file type
            allowed_types = ['audio/wav', 'audio/mp3', 'audio/flac', 'audio/m4a']
            if file.content_type not in allowed_types:
                results.append({
                    "filename": file.filename,
                    "error": f"Unsupported file type: {file.content_type}",
                    "watermark_found": False
                })
                continue
            
            # Save file temporarily and verify
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            try:
                # Initialize watermark service
                watermark_service = WatermarkService()
                
                # Detect watermark
                detection_result = await watermark_service.detect_watermark(
                    audio_path=temp_file_path,
                    method=method
                )
                
                # Store result
                verification_id = f"batch_{uuid.uuid4().hex[:12]}"
                verification = WatermarkVerification(
                    id=verification_id,
                    user_id=current_user.id,
                    original_filename=file.filename,
                    detection_method=detection_result.get('detection_method', 'unknown'),
                    watermark_found=detection_result.get('found', False),
                    watermark_id=detection_result.get('watermark_id'),
                    license_id=detection_result.get('license_id'),
                    confidence_score=detection_result.get('confidence', 0.0),
                    detection_metadata=detection_result,
                    verified_at=datetime.utcnow()
                )
                
                db.add(verification)
                
                results.append({
                    "verification_id": verification_id,
                    "filename": file.filename,
                    "watermark_found": detection_result.get('found', False),
                    "watermark_id": detection_result.get('watermark_id'),
                    "confidence_score": detection_result.get('confidence', 0.0),
                    "detection_method": detection_result.get('detection_method', 'unknown')
                })
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                
        except Exception as e:
            results.append({
                "filename": file.filename,
                "error": str(e),
                "watermark_found": False
            })
    
    # Commit all verifications
    db.commit()
    
    return {
        "batch_id": f"batch_{uuid.uuid4().hex[:12]}",
        "total_files": len(files),
        "processed_files": len(results),
        "results": results
    }

@router.get("/stats")
async def get_verification_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get verification statistics for the current user."""
    
    verifications = db.query(WatermarkVerification).filter(
        WatermarkVerification.user_id == current_user.id
    ).all()
    
    total_verifications = len(verifications)
    watermarks_found = len([v for v in verifications if v.watermark_found])
    avg_confidence = sum(v.confidence_score for v in verifications) / max(1, total_verifications)
    
    # Method breakdown
    method_stats = {}
    for verification in verifications:
        method = verification.detection_method
        if method not in method_stats:
            method_stats[method] = {'count': 0, 'found': 0}
        method_stats[method]['count'] += 1
        if verification.watermark_found:
            method_stats[method]['found'] += 1
    
    return {
        "total_verifications": total_verifications,
        "watermarks_found": watermarks_found,
        "success_rate": watermarks_found / max(1, total_verifications),
        "average_confidence": avg_confidence,
        "method_breakdown": method_stats,
        "last_verification": max(v.verified_at for v in verifications) if verifications else None
    }