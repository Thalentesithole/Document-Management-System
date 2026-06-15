from sqlalchemy import Column, String, DateTime, func, Numeric, ForeignKey, Enum
from app.models.base import Base
import enum
import uuid
from sqlalchemy.dialects.postgresql import UUID

class DocumentStatusEnum(str, enum.Enum):
    pending_extraction = "pending_extraction"           # Internal: AI processing
    pending_review = "pending_review"                   # Stage 1: Reviewer
    pending_manager_approval = "pending_manager_approval"  # Stage 2: Manager
    pending_final_approval = "pending_final_approval"   # Stage 3: Finance/Admin
    approved = "approved"
    rejected = "rejected"
    returned_to_reviewer = "returned_to_reviewer"       # Manager returned to Reviewer
    duplicate_flagged = "duplicate_flagged"
    # Legacy values still present in PostgreSQL enum type
    reviewer_approved = "reviewer_approved"
    pending_finance_approval = "pending_finance_approval"

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_name = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
    file_hash = Column(String, nullable=False, index=True)
    document_type = Column(String, nullable=True) # invoice, credit_note
    
    # Original file metadata for reliable retrieval
    original_filename = Column(String, nullable=True)  # User's original filename
    mime_type = Column(String, nullable=True)           # application/pdf, image/png, etc.
    storage_path = Column(String, nullable=True)        # Supabase bucket path for retrieval
    
    # Extracted fields
    vendor_name = Column(String, nullable=True)
    invoice_number = Column(String, nullable=True)
    invoice_date = Column(DateTime(timezone=True), nullable=True)
    
    subtotal_amount = Column(Numeric(10, 2), nullable=True)
    vat_amount = Column(Numeric(10, 2), nullable=True)
    total_amount = Column(Numeric(10, 2), nullable=True)
    currency = Column(String(3), nullable=True)
    confidence_score = Column(Numeric(5, 4), nullable=True)
    
    status = Column(Enum(DocumentStatusEnum), default=DocumentStatusEnum.pending_extraction)
    
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

