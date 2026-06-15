from sqlalchemy import Column, String, DateTime, func, ForeignKey, Numeric
from app.models.base import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

class DuplicateCheck(Base):
    __tablename__ = "duplicate_checks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    duplicate_type = Column(String, nullable=False) # exact_hash, invoice_match, vendor_amount
    confidence_score = Column(Numeric(5, 4), nullable=False) # 0.0 to 1.0
    matched_document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True)
    risk_level = Column(String, nullable=True) # high, medium, low
    created_at = Column(DateTime(timezone=True), server_default=func.now())
