import asyncio
from celery import shared_task
from app.core.database import AsyncSessionLocal
from app.models.document import Document, DocumentStatusEnum
from app.models.duplicate_check import DuplicateCheck
from sqlalchemy import select

def check_duplicates_sync(document_id: str):
    asyncio.run(check_duplicates_async(document_id))

async def check_duplicates_async(document_id: str):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Document).where(Document.id == document_id))
        document = result.scalar_one_or_none()
        if not document:
            return
            
        # Rule 1: Exact file hash match
        hash_query = select(Document).where(Document.file_hash == document.file_hash, Document.id != document.id)
        hash_res = await db.execute(hash_query)
        hash_match = hash_res.first()
        
        if hash_match:
            dup = DuplicateCheck(
                document_id=document.id,
                duplicate_type="exact_hash",
                confidence_score=1.0,
                matched_document_id=hash_match[0].id,
                risk_level="high"
            )
            db.add(dup)
            document.status = DocumentStatusEnum.duplicate_flagged
            await db.commit()
            return
            
        # Rule 2: Metadata Match (all 4 fields)
        if (document.invoice_number and document.vendor_name and 
            document.invoice_date and document.total_amount is not None):
            inv_query = select(Document).where(
                Document.invoice_number == document.invoice_number,
                Document.vendor_name == document.vendor_name,
                Document.invoice_date == document.invoice_date,
                Document.total_amount == document.total_amount,
                Document.id != document.id
            )
            inv_res = await db.execute(inv_query)
            inv_match = inv_res.first()
            if inv_match:
                 dup = DuplicateCheck(
                    document_id=document.id,
                    duplicate_type="metadata_match",
                    confidence_score=1.0,
                    matched_document_id=inv_match[0].id,
                    risk_level="high"
                 )
                 db.add(dup)
                 document.status = DocumentStatusEnum.rejected
                 
                 from app.services.audit import AuditService
                 await AuditService.log_action(
                     db=db,
                     action="duplicate_upload_attempt",
                     entity_type="Document",
                     entity_id=str(document.id),
                     user_id=document.uploaded_by,
                     new_value={
                         "attempted_filename": document.file_name,
                         "matched_document_id": str(inv_match[0].id),
                         "duplicate_type": "metadata_match"
                     }
                 )
                 
                 await db.commit()
                 return

@shared_task(name="app.tasks.duplicate.check_duplicates_task")
def check_duplicates_task(document_id: str):
    check_duplicates_sync(document_id)
