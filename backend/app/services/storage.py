import hashlib
from fastapi import UploadFile
from supabase import create_client, Client
from app.core.config import settings
import uuid

# Only initialize if credentials are provided (to avoid crashing on startup without env vars)
try:
    supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
except Exception:
    supabase = None

class StorageService:
    @staticmethod
    async def upload_document(file: UploadFile, user_id: str) -> dict:
        if not supabase:
            raise Exception("Supabase is not configured.")
        
        contents = await file.read()
        file_hash = hashlib.sha256(contents).hexdigest()
        
        await file.seek(0)
        
        file_extension = file.filename.split('.')[-1]
        unique_filename = f"{user_id}/{uuid.uuid4()}.{file_extension}"
        
        bucket_name = "documents"
        
        res = supabase.storage.from_(bucket_name).upload(
            path=unique_filename,
            file=contents,
            file_options={"content-type": file.content_type}
        )
        
        file_url = supabase.storage.from_(bucket_name).get_public_url(unique_filename)
        
        return {
            "file_name": file.filename,
            "original_filename": file.filename,
            "file_url": file_url,
            "file_hash": file_hash,
            "content_type": file.content_type,
            "storage_path": unique_filename
        }
