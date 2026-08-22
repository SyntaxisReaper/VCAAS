"""
Voice Training Service

Manages the voice training pipeline including sample validation,
model training, and deployment.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
from pathlib import Path
from loguru import logger

from app.models.mongo.user import User
from app.models.mongo.voice_sample import VoiceSample
from app.models.mongo.voice_model import VoiceModel
from app.services.audio_processor import audio_processor
from app.services.voice_models.model_registry import model_registry


class TrainingJob:
    """Represents a voice training job"""
    
    def __init__(self, job_id: str, user_id: str, voice_name: str, samples: List[str]):
        self.job_id = job_id
        self.user_id = user_id
        self.voice_name = voice_name
        self.sample_ids = samples
        self.status = "pending"
        self.progress = 0.0
        self.error_message = None
        self.created_at = datetime.utcnow()
        self.started_at = None
        self.completed_at = None
        self.result_model_id = None
        
        # Training configuration
        self.config = {
            "epochs": 100,
            "batch_size": 32,
            "learning_rate": 0.0002,
            "model_type": "xtts_v2",  # Default to XTTS v2
            "quality_target": "high",
            "validation_split": 0.1
        }
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "user_id": self.user_id,
            "voice_name": self.voice_name,
            "sample_ids": self.sample_ids,
            "status": self.status,
            "progress": self.progress,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result_model_id": self.result_model_id,
            "config": self.config
        }


class VoiceTrainingService:
    """Main voice training service"""
    
    def __init__(self):
        self.active_jobs: Dict[str, TrainingJob] = {}
        self.storage_path = Path("./storage/models")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Training queue
        self.training_queue = asyncio.Queue()
        self.is_processing = False
    
    async def start_training(
        self,
        user_id: str,
        voice_name: str,
        sample_ids: List[str],
        training_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Start a new voice training job"""
        try:
            # Validate user
            user = await User.get(user_id)
            if not user:
                raise ValueError("User not found")
            
            if not user.can_generate_voice():
                raise ValueError("User has insufficient credits or inactive subscription")
            
            # Validate samples
            samples = []
            for sample_id in sample_ids:
                sample = await VoiceSample.get(sample_id)
                if not sample:
                    raise ValueError(f"Voice sample {sample_id} not found")
                if sample.user_id != user_id:
                    raise ValueError(f"Sample {sample_id} does not belong to user")
                if not sample.is_suitable_for_training:
                    raise ValueError(f"Sample {sample_id} is not suitable for training")
                samples.append(sample)
            
            # Check minimum requirements
            if len(samples) < 3:
                raise ValueError("At least 3 high-quality samples required for training")
            
            # Calculate total training duration
            total_duration = sum(sample.duration_seconds for sample in samples)
            if total_duration < 30:  # 30 seconds minimum
                raise ValueError("Total sample duration must be at least 30 seconds")
            
            # Check user limits
            limits = user.get_monthly_limits()
            if limits["training_minutes"] != -1:  # Not unlimited
                if user.total_training_minutes + (total_duration / 60) > limits["training_minutes"]:
                    raise ValueError("Monthly training limit exceeded")
            
            # Generate job ID
            job_id = str(uuid.uuid4())
            
            # Create training job
            job = TrainingJob(job_id, user_id, voice_name, sample_ids)
            if training_config:
                job.config.update(training_config)
            
            # Store job
            self.active_jobs[job_id] = job
            
            # Add to queue
            await self.training_queue.put(job)
            
            # Start processing if not already running
            if not self.is_processing:
                asyncio.create_task(self._process_training_queue())
            
            logger.info(f"Started training job {job_id} for user {user_id}")
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to start training: {e}")
            raise
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get training job status"""
        job = self.active_jobs.get(job_id)
        return job.to_dict() if job else None
    
    async def cancel_job(self, job_id: str, user_id: str) -> bool:
        """Cancel a training job"""
        job = self.active_jobs.get(job_id)
        if not job:
            return False
        
        if job.user_id != user_id:
            raise ValueError("Cannot cancel job belonging to another user")
        
        if job.status in ["completed", "failed"]:
            return False
        
        job.status = "cancelled"
        job.error_message = "Training cancelled by user"
        logger.info(f"Cancelled training job {job_id}")
        return True
    
    async def _process_training_queue(self):
        """Process training jobs from queue"""
        self.is_processing = True
        
        try:
            while True:
                try:
                    # Get next job (wait up to 30 seconds)
                    job = await asyncio.wait_for(self.training_queue.get(), timeout=30.0)
                    
                    if job.status == "cancelled":
                        continue
                    
                    # Process the job
                    await self._execute_training_job(job)
                    
                except asyncio.TimeoutError:
                    # No jobs in queue, stop processing
                    break
                except Exception as e:
                    logger.error(f"Error in training queue processing: {e}")
                    
        finally:
            self.is_processing = False
    
    async def _execute_training_job(self, job: TrainingJob):
        """Execute a single training job"""
        try:
            job.status = "processing"
            job.started_at = datetime.utcnow()
            job.progress = 0.0
            
            logger.info(f"Starting training job {job.job_id}")
            
            # Step 1: Load and validate samples (10%)
            await self._update_progress(job, 0.1, "Loading voice samples...")
            samples = []
            for sample_id in job.sample_ids:
                sample = await VoiceSample.get(sample_id)
                if sample:
                    samples.append(sample)
            
            # Step 2: Prepare training data (20%)
            await self._update_progress(job, 0.2, "Preparing training data...")
            training_data = await self._prepare_training_data(samples, job)
            
            # Step 3: Initialize model (30%)
            await self._update_progress(job, 0.3, "Initializing training model...")
            model_type = job.config.get("model_type", "xtts_v2")
            
            # Step 4: Train model (30% - 90%)
            await self._update_progress(job, 0.4, "Training voice model...")
            model_result = await self._train_model(training_data, job, model_type)
            
            # Step 5: Validate and deploy (90% - 100%)
            await self._update_progress(job, 0.9, "Validating and deploying model...")
            model_id = await self._deploy_trained_model(model_result, job, samples)
            
            # Complete job
            job.status = "completed"
            job.progress = 1.0
            job.completed_at = datetime.utcnow()
            job.result_model_id = model_id
            
            # Update user statistics
            user = await User.get(job.user_id)
            if user:
                total_duration = sum(sample.duration_seconds for sample in samples)
                await user.update_usage(training_minutes=total_duration / 60)
            
            logger.info(f"Completed training job {job.job_id} -> model {model_id}")
            
        except Exception as e:
            logger.error(f"Training job {job.job_id} failed: {e}")
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
    
    async def _update_progress(self, job: TrainingJob, progress: float, status_message: str):
        """Update job progress"""
        job.progress = progress
        logger.info(f"Job {job.job_id}: {progress*100:.1f}% - {status_message}")
        
        # In a real implementation, you might want to broadcast this to websockets
        # or store progress updates in the database for real-time updates
    
    async def _prepare_training_data(
        self, 
        samples: List[VoiceSample], 
        job: TrainingJob
    ) -> Dict[str, Any]:
        """Prepare audio samples for training"""
        try:
            training_files = []
            
            for sample in samples:
                # Get sample file path
                if not os.path.exists(sample.file_path):
                    raise ValueError(f"Sample file not found: {sample.file_path}")
                
                # Read and process audio
                with open(sample.file_path, 'rb') as f:
                    audio_data = f.read()
                
                # Enhance for training
                enhanced_audio = await audio_processor.enhance_audio_for_training(audio_data)
                
                # Save enhanced version temporarily
                temp_path = self.storage_path / f"job_{job.job_id}" / f"enhanced_{sample.id}.wav"
                temp_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(temp_path, 'wb') as f:
                    f.write(enhanced_audio)
                
                training_files.append({
                    "path": str(temp_path),
                    "transcription": sample.transcription or "",
                    "duration": sample.duration_seconds,
                    "quality_score": sample.quality_score or 0.8
                })
            
            return {
                "files": training_files,
                "total_duration": sum(f["duration"] for f in training_files),
                "average_quality": sum(f["quality_score"] for f in training_files) / len(training_files)
            }
            
        except Exception as e:
            logger.error(f"Training data preparation failed: {e}")
            raise
    
    async def _train_model(
        self, 
        training_data: Dict[str, Any], 
        job: TrainingJob,
        model_type: str
    ) -> Dict[str, Any]:
        """Train the voice model"""
        try:
            # For now, simulate training with different approaches based on model type
            if model_type == "elevenlabs":
                return await self._train_with_elevenlabs(training_data, job)
            elif model_type == "xtts_v2":
                return await self._train_with_xtts(training_data, job)
            else:
                # Generic training simulation
                return await self._simulate_training(training_data, job)
                
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            raise
    
    async def _train_with_elevenlabs(
        self, 
        training_data: Dict[str, Any], 
        job: TrainingJob
    ) -> Dict[str, Any]:
        """Train using ElevenLabs voice cloning"""
        try:
            # Load ElevenLabs model
            model = await model_registry.load_model("elevenlabs_multilingual")
            if not model:
                raise ValueError("ElevenLabs model not available")
            
            # Prepare audio samples
            audio_samples = []
            for file_info in training_data["files"]:
                with open(file_info["path"], 'rb') as f:
                    audio_samples.append(f.read())
            
            # Clone voice using ElevenLabs
            voice_id = await model.clone_voice(
                audio_samples, 
                job.voice_name,
                f"Custom voice trained for user {job.user_id}"
            )
            
            return {
                "model_type": "elevenlabs",
                "voice_id": voice_id,
                "model_files": {},  # ElevenLabs is API-based
                "training_metrics": {
                    "samples_used": len(audio_samples),
                    "total_duration": training_data["total_duration"],
                    "quality_score": training_data["average_quality"]
                }
            }
            
        except Exception as e:
            logger.error(f"ElevenLabs training failed: {e}")
            raise
    
    async def _train_with_xtts(
        self, 
        training_data: Dict[str, Any], 
        job: TrainingJob
    ) -> Dict[str, Any]:
        """Train using XTTS (simulated for now)"""
        try:
            # Simulate XTTS training process
            epochs = job.config.get("epochs", 100)
            
            # Simulate training progress
            for epoch in range(1, epochs + 1):
                # Update progress (40% to 85% of total job progress)
                progress = 0.4 + (epoch / epochs) * 0.45
                await self._update_progress(
                    job, 
                    progress, 
                    f"Training epoch {epoch}/{epochs}"
                )
                
                # Simulate training time
                await asyncio.sleep(0.1)  # Much faster for demo
            
            # Generate model files
            model_dir = self.storage_path / f"model_{job.job_id}"
            model_dir.mkdir(parents=True, exist_ok=True)
            
            # Simulate saving model files
            model_files = {
                "config.json": str(model_dir / "config.json"),
                "model.pth": str(model_dir / "model.pth"),
                "vocab.json": str(model_dir / "vocab.json")
            }
            
            # Create dummy files for now
            for file_type, file_path in model_files.items():
                with open(file_path, 'w') as f:
                    f.write(f"# {file_type} for {job.voice_name}\n")
            
            return {
                "model_type": "xtts_v2",
                "model_files": model_files,
                "training_metrics": {
                    "epochs": epochs,
                    "final_loss": 0.023,  # Simulated
                    "quality_score": 0.89,  # Simulated
                    "samples_used": len(training_data["files"]),
                    "total_duration": training_data["total_duration"]
                }
            }
            
        except Exception as e:
            logger.error(f"XTTS training failed: {e}")
            raise
    
    async def _simulate_training(
        self, 
        training_data: Dict[str, Any], 
        job: TrainingJob
    ) -> Dict[str, Any]:
        """Simulate generic training process"""
        try:
            # Simulate training steps
            steps = 50
            for step in range(steps):
                progress = 0.4 + (step / steps) * 0.45
                await self._update_progress(
                    job, 
                    progress, 
                    f"Training step {step + 1}/{steps}"
                )
                await asyncio.sleep(0.05)  # Simulate work
            
            return {
                "model_type": "simulated",
                "model_files": {},
                "training_metrics": {
                    "samples_used": len(training_data["files"]),
                    "quality_score": training_data["average_quality"],
                    "status": "completed"
                }
            }
            
        except Exception as e:
            logger.error(f"Simulated training failed: {e}")
            raise
    
    async def _deploy_trained_model(
        self,
        model_result: Dict[str, Any],
        job: TrainingJob,
        samples: List[VoiceSample]
    ) -> str:
        """Deploy trained model and create VoiceModel document"""
        try:
            # Create VoiceModel document
            voice_model = VoiceModel(
                name=job.voice_name,
                description=f"Custom voice model trained from {len(samples)} samples",
                user_id=job.user_id,
                is_public=False,
                training_samples=[str(sample.id) for sample in samples],
                training_duration_minutes=sum(sample.duration_seconds for sample in samples) / 60,
                sample_count=len(samples),
                model_type=model_result["model_type"],
                model_version="1.0.0",
                architecture=model_result["model_type"],
                model_files=model_result.get("model_files", {}),
                model_size_mb=self._calculate_model_size(model_result.get("model_files", {})),
                training_config=job.config,
                status="completed",
                deployment_status="deployed",
                training_started_at=job.started_at,
                training_completed_at=datetime.utcnow(),
                deployed_at=datetime.utcnow()
            )
            
            # Add training metrics
            metrics = model_result.get("training_metrics", {})
            voice_model.quality_score = metrics.get("quality_score", 0.8)
            voice_model.similarity_score = metrics.get("similarity_score", 0.85)
            voice_model.naturalness_score = metrics.get("naturalness_score", 0.82)
            voice_model.training_loss = metrics.get("final_loss", 0.05)
            
            # Detect voice characteristics from samples
            voice_model.supported_languages = ["en"]  # Default
            if samples:
                # Analyze first sample for characteristics
                first_sample = samples[0]
                if first_sample.language_detected:
                    voice_model.supported_languages = [first_sample.language_detected]
            
            # Save to database
            await voice_model.save()
            
            # Update sample usage statistics
            for sample in samples:
                await sample.update_usage_stats("training")
            
            logger.info(f"Deployed voice model {voice_model.id} from job {job.job_id}")
            return str(voice_model.id)
            
        except Exception as e:
            logger.error(f"Model deployment failed: {e}")
            raise
    
    def _calculate_model_size(self, model_files: Dict[str, str]) -> float:
        """Calculate total size of model files in MB"""
        total_size = 0
        for file_path in model_files.values():
            if os.path.exists(file_path):
                total_size += os.path.getsize(file_path)
        
        return total_size / (1024 * 1024)  # Convert to MB
    
    async def list_user_jobs(
        self, 
        user_id: str, 
        status_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List training jobs for a user"""
        user_jobs = []
        
        for job in self.active_jobs.values():
            if job.user_id == user_id:
                if status_filter is None or job.status == status_filter:
                    user_jobs.append(job.to_dict())
        
        # Sort by creation time (newest first)
        user_jobs.sort(key=lambda x: x["created_at"], reverse=True)
        return user_jobs
    
    async def cleanup_completed_jobs(self, max_age_days: int = 7):
        """Clean up old completed jobs"""
        cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)
        
        jobs_to_remove = []
        for job_id, job in self.active_jobs.items():
            if (job.status in ["completed", "failed", "cancelled"] and 
                job.completed_at and 
                job.completed_at < cutoff_date):
                jobs_to_remove.append(job_id)
        
        for job_id in jobs_to_remove:
            del self.active_jobs[job_id]
            logger.info(f"Cleaned up old training job {job_id}")
    
    def get_training_stats(self) -> Dict[str, Any]:
        """Get training service statistics"""
        total_jobs = len(self.active_jobs)
        status_counts = {}
        
        for job in self.active_jobs.values():
            status_counts[job.status] = status_counts.get(job.status, 0) + 1
        
        return {
            "total_jobs": total_jobs,
            "status_counts": status_counts,
            "queue_size": self.training_queue.qsize(),
            "is_processing": self.is_processing
        }


# Global training service instance
voice_training_service = VoiceTrainingService()