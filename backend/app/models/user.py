from sqlalchemy import Column, String, Boolean, DateTime, func, Enum
from app.models.base import Base
import enum
import uuid
from sqlalchemy.dialects.postgresql import UUID

class RoleEnum(str, enum.Enum):
    admin = "admin"
    reviewer = "reviewer"
    approver = "approver"
    manager = "manager"
    viewer = "viewer"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=True) # nullable if using Supabase Auth
    full_name = Column(String, nullable=True)
    role = Column(Enum(RoleEnum), default=RoleEnum.reviewer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), index=True, nullable=False)
    token_hash = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
