import pytest
import io
from httpx import AsyncClient
from unittest.mock import patch

@pytest.mark.asyncio
async def test_list_documents_unauthenticated(async_client: AsyncClient):
    resp = await async_client.get("/api/v1/documents/")
    assert resp.status_code == 401

@pytest.mark.asyncio
async def test_list_documents_authenticated(admin_client: AsyncClient, sample_document):
    resp = await admin_client.get("/api/v1/documents/")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1

@pytest.mark.asyncio
async def test_viewer_sees_only_own_documents(viewer_client: AsyncClient, viewer_user, db_session, sample_document):
    # sample_document is owned by admin
    resp = await viewer_client.get("/api/v1/documents/")
    assert resp.status_code == 200
    assert len(resp.json()) == 0

@pytest.mark.asyncio
async def test_get_document_by_id(admin_client: AsyncClient, sample_document):
    resp = await admin_client.get(f"/api/v1/documents/{sample_document.id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == str(sample_document.id)

@pytest.mark.asyncio
async def test_get_document_not_found(admin_client: AsyncClient):
    resp = await admin_client.get("/api/v1/documents/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404

@pytest.mark.asyncio
@patch("app.api.documents.StorageService.upload_document")
@patch("app.api.documents.process_document.delay")
async def test_upload_pdf_accepted(mock_process, mock_upload, admin_client: AsyncClient, admin_user):
    mock_upload.return_value = {
        "file_name": "test.pdf",
        "file_url": "https://fake.url/test.pdf",
        "file_hash": "dummyhash",
        "content_type": "application/pdf"
    }
    file = ("test.pdf", io.BytesIO(b"dummy pdf content"), "application/pdf")
    resp = await admin_client.post(
        "/api/v1/documents/upload",
        files={"file": file}
    )
    assert resp.status_code == 200
    assert "Extraction started" in resp.json()["message"] or "extraction started" in resp.json()["message"].lower()
    mock_process.assert_called_once()

@pytest.mark.asyncio
async def test_upload_txt_rejected(admin_client: AsyncClient):
    file = ("test.txt", io.BytesIO(b"dummy"), "text/plain")
    resp = await admin_client.post(
        "/api/v1/documents/upload",
        files={"file": file}
    )
    assert resp.status_code == 400
    assert "Unsupported file format" in resp.json()["detail"]
