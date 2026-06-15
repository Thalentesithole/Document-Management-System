from sqlalchemy import Column, String, DateTime, func, ForeignKey, Integer
from app.models.base import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

class ApprovalWorkflow(Base):
    __tablename__ = "approval_workflows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    stage_number = Column(Integer, nullable=False) # 1, 2, 3
    approver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False) # approve, reject
    comments = Column(String, nullable=True)
    approved_at = Column(DateTime(timezone=True), server_default=func.now())
