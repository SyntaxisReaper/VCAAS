"""
License SQLAlchemy model for VCaaS platform.

Fields inferred from:
  - api/v1/licenses.py  (create, list, get, update, token endpoints)
  - schemas/license.py  (LicenseCreate, LicenseResponse)
  - services/license_service.py
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, Numeric, String
from sqlalchemy.orm import relationship

from app.core.database import Base


def _new_id() -> str:
    return f"lic_{uuid.uuid4().hex[:16]}"


class License(Base):
    __tablename__ = "licenses"

    # Primary key
    id = Column(String(64), primary_key=True, default=_new_id)

    # Ownership
    user_id = Column(String(32), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    voice_id = Column(String(64), ForeignKey("voices.id", ondelete="CASCADE"), nullable=False, index=True)

    # Metadata
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)

    # License type: personal | commercial | enterprise | educational | non_profit | custom
    license_type = Column(String(50), nullable=False)

    # Pricing
    price = Column(Numeric(10, 2), nullable=True)
    currency = Column(String(3), default="USD", nullable=False)

    # Usage constraints
    duration_days = Column(Integer, nullable=True)    # None = perpetual
    usage_limit = Column(Integer, nullable=True)       # None = unlimited

    # Scope constraints (stored as JSON arrays / objects)
    territory = Column(JSON, nullable=True)            # List[str] of ISO country codes
    allowed_use_cases = Column(JSON, nullable=True)    # List[str]
    restrictions = Column(JSON, nullable=True)         # Dict[str, Any]

    # State
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    owner = relationship("User", back_populates="licenses")
    voice = relationship("Voice", back_populates="licenses")
    usages = relationship("LicenseUsage", back_populates="license", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<License id={self.id!r} type={self.license_type!r} active={self.is_active}>"
