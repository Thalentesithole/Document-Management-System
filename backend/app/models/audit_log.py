from sqlalchemy import Column, String, DateTime, func, ForeignKey, JSON
from app.models.base import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.postgresql import JSONB

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False) # upload, approve, login, etc.
    entity_type = Column(String, nullable=False) # Document, User, etc.
    entity_id = Column(String, nullable=False)
    old_value = Column(JSON().with_variant(JSONB, "postgresql"), nullable=True)
    new_value = Column(JSON().with_variant(JSONB, "postgresql"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
