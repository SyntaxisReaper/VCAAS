"""
Text-to-Speech Service (in-memory, minimal implementation)

Provides a simple job manager and synthesis stub to align with API v1.
Generates synthetic WAV/MP3/OGG output and tracks jobs in-memory.
"""

import os
import io
import asyncio
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import soundfile as sf
from loguru import logger


class TTSService:
    """Lightweight TTS job service with synthetic audio generation."""

    def __init__(self) -> None:
        self._jobs: Dict[str, Dict[str, Any]] = {}
        self._model_loaded: bool = True
        self._output_dir = Path("data/tts_outputs")
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._stats: Dict[str, Any] = {
            "total_jobs": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0,
            "total_duration": 0.0,
        }

    # Optional lifecycle hooks (used by main.py)
    async def initialize(self) -> None:
        self._model_loaded = True

    async def cleanup_old_jobs(self, max_age_minutes: int = 60) -> None:
        cutoff = datetime.utcnow() - timedelta(minutes=max_age_minutes)
        to_remove = []
        for job_id, job in self._jobs.items():
            ts = job.get("created_at")
            if isinstance(ts, datetime) and ts < cutoff:
                to_remove.append(job_id)
        for j in to_remove:
            self._jobs.pop(j, None)

    # High-level stats
    def get_service_stats(self) -> Dict[str, Any]:
        return {
            **self._stats,
            "active_jobs": len([j for j in self._jobs.values() if j["status"] in {"pending", "processing"}]),
        }

    # API used by v1/tts endpoints (jobful API)
    async def generate_speech(
        self,
        user_id: str,
        voice_model_id: str,
        text: str,
        output_format: str = "wav",
        voice_settings: Optional[Dict[str, Any]] = None,
    ) -> str:
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        if output_format not in {"wav", "mp3", "ogg"}:
            raise ValueError("Unsupported output format")

        job_id = f"tts_{uuid.uuid4().hex[:12]}"
        created_at = datetime.utcnow()
        estimated_duration = max(1.0, min(60.0, len(text) * 0.06))
        estimated_cost = round(len(text) / 1000.0 * 0.02, 4)

        self._jobs[job_id] = {
            "job_id": job_id,
            "user_id": user_id,
            "voice_model_id": voice_model_id,
            "text": text,
            "output_format": output_format,
            "voice_settings": voice_settings or {},
            "status": "pending",
            "progress": 0,
            "created_at": created_at,
            "estimated_duration": estimated_duration,
            "estimated_cost": estimated_cost,
        }
        self._stats["total_jobs"] += 1

        # Fire-and-forget processing
        asyncio.create_task(self._process_job(job_id))
        return job_id

    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self._jobs.get(job_id)

    async def cancel_job(self, job_id: str, user_id: str) -> bool:
        job = self._jobs.get(job_id)
        if not job:
            return False
        if job["user_id"] != user_id:
            raise ValueError("Access denied")
        if job["status"] in {"completed", "failed", "cancelled"}:
            return False
        job["status"] = "cancelled"
        job["completed_at"] = datetime.utcnow()
        self._stats["cancelled"] += 1
        return True

    async def get_job_result(self, job_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        job = self._jobs.get(job_id)
        if not job or job["user_id"] != user_id:
            return None
        if job.get("status") != "completed" or not job.get("output_file"):
            return None
        return {
            "job_id": job_id,
            "status": job["status"],
            "output_file": job["output_file"],
            "duration": job.get("actual_duration"),
            "file_size_mb": job.get("file_size_mb"),
            "quality_score": job.get("quality_score"),
            "created_at": job.get("created_at").isoformat() if job.get("created_at") else None,
            "completed_at": job.get("completed_at").isoformat() if job.get("completed_at") else None,
        }

    async def list_user_jobs(self, user_id: str, status_filter: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        rows = [j for j in self._jobs.values() if j["user_id"] == user_id]
        if status_filter:
            rows = [j for j in rows if j["status"] == status_filter]
        rows.sort(key=lambda x: x.get("created_at") or datetime.min, reverse=True)
        return rows[:limit]

    # API used by v1/tts synthesize_speech (stateless one-shot)
    async def synthesize_text(
        self,
        text: str,
        voice_id: str,
        speaker_embedding: Optional[List[float]] = None,
        voice_params: Optional[Dict[str, Any]] = None,
        job_id: Optional[str] = None,
    ) -> str:
        """Generate a small WAV file and return its path."""
        voice_params = voice_params or {}
        speed = float(voice_params.get("speed", 1.0))
        pitch = float(voice_params.get("pitch", 0.0))
        duration = max(1.0, min(30.0, len(text) * 0.06 / max(speed, 0.1)))
        sr = 22050
        t = np.linspace(0, duration, int(sr * duration), endpoint=False)
        base = 180.0 + (np.mean(speaker_embedding) * 50.0 if speaker_embedding else 0.0) + pitch * 50.0
        wave = (
            0.3 * np.sin(2 * np.pi * base * t)
            + 0.2 * np.sin(2 * np.pi * (base * 2) * t)
            + 0.1 * np.sin(2 * np.pi * (base * 3) * t)
        )
        wave += np.random.normal(0, 0.01, size=wave.shape)
        wave = (wave / (np.max(np.abs(wave)) + 1e-6) * 0.8).astype(np.float32)

        out_path = self._output_dir / f"{job_id or 'synth'}_{voice_id}.wav"
        sf.write(str(out_path), wave, sr)
        return str(out_path)

    async def _process_job(self, job_id: str) -> None:
        job = self._jobs.get(job_id)
        if not job or job.get("status") == "cancelled":
            return
        try:
            job["status"] = "processing"
            job["progress"] = 10

            # Synthesize audio
            wav_path = await self.synthesize_text(
                text=job["text"],
                voice_id=job.get("voice_model_id", "default"),
                speaker_embedding=None,
                voice_params=job.get("voice_settings"),
                job_id=job_id,
            )
            job["progress"] = 70

            # Optionally convert format (only wav implemented realistically)
            output_path = wav_path
            if job["output_format"] != "wav":
                # For simplicity, keep WAV but reflect extension
                new_path = Path(wav_path).with_suffix(f".{job['output_format']}")
                os.replace(wav_path, new_path)
                output_path = str(new_path)

            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            duration = max(1.0, len(job["text"]) * 0.06)

            job.update(
                {
                    "status": "completed",
                    "progress": 100,
                    "output_file": output_path,
                    "completed_at": datetime.utcnow(),
                    "actual_duration": duration,
                    "file_size_mb": round(size_mb, 4),
                    "quality_score": 0.85,
                    "audio_url": f"/api/v1/tts/job/{job_id}/download",
                }
            )
            self._stats["completed"] += 1
            self._stats["total_duration"] += duration
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}")
            job.update(
                {
                    "status": "failed",
                    "progress": 100,
                    "error_message": str(e),
                    "completed_at": datetime.utcnow(),
                }
            )
            self._stats["failed"] += 1


# Module-level singleton for easy import in routers
tts_service = TTSService()
