"""
User SQLAlchemy model for VCaaS platform.

Fields inferred from:
  - api/v1/auth.py  (register, login, profile endpoints)
  - schemas/auth.py (UserCreate, UserResponse)
  - services/auth.py
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.orm import relationship

from app.core.database import Base


def _new_id() -> str:
    return uuid.uuid4().hex


class User(Base):
    __tablename__ = "users"

    # Primary key — short hex string for readability in logs
    id = Column(String(32), primary_key=True, default=_new_id)

    # Identity
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)

    # Auth — nullable so Firebase-only users don't need a local password
    hashed_password = Column(String(255), nullable=True)

    # Firebase uid — nullable for password-only users
    firebase_uid = Column(String(128), unique=True, nullable=True, index=True)

    # Profile
    full_name = Column(String(255), nullable=True)

    # Flags
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_premium = Column(Boolean, default=False, nullable=False)

    # Subscription
    subscription_tier = Column(String(50), default="free", nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    voices = relationship("Voice", back_populates="owner", cascade="all, delete-orphan")
    licenses = relationship("License", back_populates="owner", cascade="all, delete-orphan")
    usage_logs = relationship("UsageLog", back_populates="user", cascade="all, delete-orphan")
    watermark_verifications = relationship(
        "WatermarkVerification", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id!r} email={self.email!r}>"
