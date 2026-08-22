"""
Voice SQLAlchemy model for VCaaS platform.

Fields inferred from:
  - api/v1/voices.py  (upload, list, get, update, delete endpoints)
  - schemas/voice.py  (VoiceResponse, VoiceUploadResponse)
  - services/voice_processor.py
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from app.core.database import Base


def _new_id() -> str:
    return f"voice_{uuid.uuid4().hex[:12]}"


class Voice(Base):
    __tablename__ = "voices"

    # Primary key — prefixed for readability
    id = Column(String(64), primary_key=True, default=_new_id)

    # Ownership
    user_id = Column(String(32), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Metadata
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    original_filename = Column(String(512), nullable=True)

    # File storage
    file_path = Column(String(1024), nullable=True)   # local or GCS/S3 path
    storage_bucket = Column(String(255), nullable=True)
    storage_key = Column(String(1024), nullable=True)

    # ML artifacts
    speaker_embedding = Column(JSON, nullable=True)   # List[float], stored as JSON array

    # Audio properties
    duration = Column(Float, nullable=False, default=0.0)
    sample_rate = Column(Integer, nullable=True)
    file_size = Column(Integer, nullable=True)         # bytes

    # Processing state
    status = Column(String(50), default="processing", nullable=False, index=True)
    # Allowed values: processing | ready | failed | archived

    quality_score = Column(Float, nullable=True)       # 0.0–1.0

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    owner = relationship("User", back_populates="voices")
    licenses = relationship("License", back_populates="voice", cascade="all, delete-orphan")
    usage_logs = relationship("UsageLog", back_populates="voice", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Voice id={self.id!r} name={self.name!r} status={self.status!r}>"
