"""
WatermarkVerification SQLAlchemy model for VCaaS platform.

Records every watermark detection/verification event.

Fields inferred from:
  - api/v1/verify.py         (WatermarkVerification usage)
  - schemas/watermark.py     (WatermarkVerificationResponse)
  - core/watermark.py        (WatermarkService detection output)
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, JSON, String
from sqlalchemy.orm import relationship

from app.core.database import Base


def _new_id() -> str:
    return f"verify_{uuid.uuid4().hex[:16]}"


class WatermarkVerification(Base):
    """Audit record for every watermark detection request."""

    __tablename__ = "watermark_verifications"

    id = Column(String(64), primary_key=True, default=_new_id)

    # Who requested the verification (nullable — API can be called unauthenticated in some configs)
    user_id = Column(String(32), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Submitted file info
    audio_filename = Column(String(512), nullable=True)
    audio_content_type = Column(String(100), nullable=True)

    # Detection result
    watermark_found = Column(Boolean, nullable=False, default=False)
    watermark_id = Column(String(64), nullable=True, index=True)   # ID embedded in audio
    license_id = Column(String(64), nullable=True)                  # license the watermark references
    confidence_score = Column(Float, nullable=False, default=0.0)
    signature_valid = Column(Boolean, nullable=False, default=False)

    # Method used: mvp_sine | robust_spread_spectrum | auto
    detection_method = Column(String(50), nullable=False, default="auto")

    # Full detection payload (raw dict from WatermarkService)
    result_metadata = Column(JSON, nullable=True)

    # Timestamp
    verified_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="watermark_verifications")

    def __repr__(self) -> str:
        return (
            f"<WatermarkVerification id={self.id!r} "
            f"found={self.watermark_found} confidence={self.confidence_score:.2f}>"
        )
