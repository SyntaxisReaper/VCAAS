"""
Usage log SQLAlchemy models for VCaaS platform.

Two models:
  - UsageLog       — records every TTS synthesis event (imported by tts.py as `UsageLog`)
  - LicenseUsage   — records every license token consumption event (imported by licenses.py as `LicenseUsage`)

Fields inferred from:
  - api/v1/tts.py       (UsageLog usage)
  - api/v1/licenses.py  (LicenseUsage usage)
  - schemas/license.py  (LicenseUsageResponse)
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from app.core.database import Base


def _new_id() -> str:
    return uuid.uuid4().hex


class UsageLog(Base):
    """Records every TTS synthesis attempt for analytics and billing."""

    __tablename__ = "usage_logs"

    id = Column(String(32), primary_key=True, default=_new_id)

    # Who / what
    user_id = Column(String(32), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    voice_id = Column(String(64), ForeignKey("voices.id", ondelete="SET NULL"), nullable=True, index=True)
    license_id = Column(String(64), ForeignKey("licenses.id", ondelete="SET NULL"), nullable=True)

    # Synthesis details
    text_length = Column(Integer, nullable=False, default=0)
    audio_duration = Column(Float, nullable=True)      # seconds
    watermark_id = Column(String(64), nullable=True)
    synthesis_method = Column(String(50), nullable=True)  # zero_shot | finetuned | fallback

    # Request metadata (IP, API key, etc.)
    request_metadata = Column(JSON, nullable=True)

    # Status: success | error | quota_exceeded
    status = Column(String(20), default="success", nullable=False)
    error_message = Column(String(1000), nullable=True)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="usage_logs")
    voice = relationship("Voice", back_populates="usage_logs")

    def __repr__(self) -> str:
        return f"<UsageLog id={self.id!r} user_id={self.user_id!r} status={self.status!r}>"


class LicenseUsage(Base):
    """Records every license token consumption event."""

    __tablename__ = "license_usages"

    id = Column(String(32), primary_key=True, default=_new_id)

    # License / token refs
    license_id = Column(String(64), ForeignKey("licenses.id", ondelete="CASCADE"), nullable=False, index=True)
    token_id = Column(String(255), nullable=True, index=True)

    # Consumer identity
    user_id = Column(String(32), nullable=True)      # may be external user — no FK constraint
    voice_id = Column(String(64), nullable=True)

    # Usage details
    text_length = Column(Integer, nullable=False, default=0)
    audio_duration = Column(Float, nullable=True)
    watermark_id = Column(String(64), nullable=True)

    # Arbitrary extra metadata from the request
    meta_data = Column(JSON, nullable=True)

    # Timestamp
    used_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    license = relationship("License", back_populates="usages")

    def __repr__(self) -> str:
        return f"<LicenseUsage id={self.id!r} license_id={self.license_id!r}>"
