from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.user import User, RoleEnum
from app.models.document import Document
from app.api.deps import get_current_user, require_roles
from app.services.storage import StorageService
from app.services.audit import AuditService
from app.tasks.extraction import process_document
import uuid
import hashlib

router = APIRouter()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not file.filename.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg')):
        raise HTTPException(status_code=400, detail="Unsupported file format. Only PDF, PNG, JPG, and JPEG are allowed.")
        
    # Size validation (Max 10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024 # 10MB
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File exceeds maximum size of 10MB")
    try:
        file_bytes = await file.read()
        
        # --- DUPLICATE CHECK: Hash-based (pre-storage) ---
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        existing = await db.execute(
            select(Document).where(Document.file_hash == file_hash)
        )
        existing_doc = existing.scalar_one_or_none()
        
        if existing_doc:
            # Log the duplicate attempt in audit
            await AuditService.log_action(
                db=db,
                action="duplicate_upload_attempt",
                entity_type="Document",
                entity_id=str(existing_doc.id),
                user_id=current_user.id,
                new_value={
                    "attempted_filename": file.filename,
                    "matched_document_id": str(existing_doc.id),
                    "matched_filename": existing_doc.file_name,
                    "duplicate_type": "exact_hash"
                }
            )
            raise HTTPException(
                status_code=409,
                detail="Duplicate document detected. This invoice already exists in the system."
            )
        
        # --- CLASSIFICATION: Synchronous using Gemini ---
        import os
        from google import genai
        from google.genai import types
        from app.core.config import settings
        
        classification = None
        if settings.GEMINI_API_KEY:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
            mime_type = 'application/pdf'
            if file.filename.lower().endswith('.png'):
                mime_type = 'image/png'
            elif file.filename.lower().endswith(('.jpg', '.jpeg')):
                mime_type = 'image/jpeg'
                
            prompt = """
            Analyze this document and classify it.
            Output ONLY ONE of the following three exact words based on the document type:
            invoice
            credit_note
            unknown
            
            Do not output any other text.
            """
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                    prompt
                ]
            )
            classification = response.text.strip().lower()
            
            if classification not in ['invoice', 'credit_note']:
                raise HTTPException(status_code=400, detail="Only invoices and credit notes may be uploaded.")
                
        # Reset file pointer for StorageService
        await file.seek(0)
        
        storage_info = await StorageService.upload_document(file, str(current_user.id))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage error: {e}")
        
    document = Document(
        file_name=storage_info["file_name"],
        file_url=storage_info["file_url"],
        file_hash=storage_info["file_hash"],
        document_type=classification,  # Store AI classification, not MIME type
        original_filename=storage_info["original_filename"],
        mime_type=storage_info["content_type"],
        storage_path=storage_info["storage_path"],
        uploaded_by=current_user.id
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    
    await AuditService.log_action(
        db=db,
        action="upload",
        entity_type="Document",
        entity_id=str(document.id),
        user_id=current_user.id
    )
    
    # Trigger Extraction Agent
    process_document.delay(str(document.id))
    
    return {"message": "Upload successful, extraction started", "document_id": document.id}

@router.get("/{id}/download")
async def download_document(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Download the original uploaded file with correct content type and filename."""
    result = await db.execute(select(Document).where(Document.id == id))
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Try to fetch the file from Supabase storage
    try:
        from app.services.storage import supabase
        if not supabase:
            raise HTTPException(status_code=500, detail="Storage not configured")
        
        bucket_name = "documents"
        
        if document.storage_path:
            file_bytes = supabase.storage.from_(bucket_name).download(document.storage_path)
        else:
            # Fallback: try to download using the file_url directly
            import httpx
            async with httpx.AsyncClient() as http_client:
                resp = await http_client.get(document.file_url)
                if resp.status_code != 200:
                    raise HTTPException(status_code=404, detail="File not found in storage")
                file_bytes = resp.content
        
        # Determine content type
        content_type = document.mime_type or "application/octet-stream"
        filename = document.original_filename or document.file_name
        
        return Response(
            content=file_bytes,
            media_type=content_type,
            headers={
                "Content-Disposition": f'inline; filename="{filename}"',
                "X-Document-Id": str(document.id)
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve file: {e}")

@router.get("/{id}")
async def get_document(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Document).where(Document.id == id))
    document = result.scalar_one_or_none()
    if not document:
         raise HTTPException(status_code=404, detail="Not found")
    return document

@router.get("/")
async def list_documents(
    skip: int = 0, limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(Document).offset(skip).limit(limit)
         
    result = await db.execute(query)
    return result.scalars().all()

