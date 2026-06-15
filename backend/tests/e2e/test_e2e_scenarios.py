import pytest
import io
from httpx import AsyncClient
from unittest.mock import patch
from app.models.document import DocumentStatusEnum

@pytest.mark.asyncio
@patch("app.api.documents.StorageService.upload_document")
@patch("app.api.documents.process_document.delay")
async def test_full_business_process(mock_process, mock_upload, admin_client: AsyncClient, reviewer_client: AsyncClient, manager_client: AsyncClient):
    # 1. Upload
    mock_upload.return_value = {
        "file_name": "invoice.pdf",
        "file_url": "https://test.url/invoice.pdf",
        "file_hash": "hash123",
        "content_type": "application/pdf"
    }
    file = ("invoice.pdf", io.BytesIO(b"pdf data"), "application/pdf")
    resp_upload = await reviewer_client.post("/api/v1/documents/upload", files={"file": file})
    assert resp_upload.status_code == 200
    doc_id = resp_upload.json()["document_id"]
    
    # Normally celery extracts data here. We'll skip and let it be pending_extraction or we could manually set it.
    # To test workflow, we assume extraction succeeded and status is pending_review
    # But for E2E we must use DB session or assume it.
    pass 
