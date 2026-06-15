import pytest
import uuid
from httpx import AsyncClient
from tests.fixtures.factories import DocumentFactory
from app.models.document import DocumentStatusEnum

@pytest.mark.asyncio
async def test_approve_pending_review(admin_client: AsyncClient, db_session, viewer_user):
    doc = DocumentFactory.build(uploaded_by=viewer_user.id, status=DocumentStatusEnum.pending_review)
    db_session.add(doc)
    await db_session.commit()
    await db_session.refresh(doc)

    resp = await admin_client.post(f"/api/v1/workflow/{doc.id}/approve", json={"comments": "looks good"})
    assert resp.status_code == 200
    assert resp.json()["status"] == DocumentStatusEnum.pending_manager_approval

@pytest.mark.asyncio
async def test_reject_returns_rejected_status(admin_client: AsyncClient, db_session, viewer_user):
    doc = DocumentFactory.build(uploaded_by=viewer_user.id, status=DocumentStatusEnum.pending_review)
    db_session.add(doc)
    await db_session.commit()
    await db_session.refresh(doc)

    resp = await admin_client.post(f"/api/v1/workflow/{doc.id}/reject", json={"comments": "bad"})
    assert resp.status_code == 200
    assert resp.json()["status"] == DocumentStatusEnum.rejected

@pytest.mark.asyncio
async def test_approve_own_submission(admin_client: AsyncClient, admin_user, db_session):
    doc = DocumentFactory.build(uploaded_by=admin_user.id, status=DocumentStatusEnum.pending_review)
    db_session.add(doc)
    await db_session.commit()
    await db_session.refresh(doc)

    resp = await admin_client.post(f"/api/v1/workflow/{doc.id}/approve", json={"comments": ""})
    assert resp.status_code == 403

@pytest.mark.asyncio
async def test_approve_nonexistent_document(admin_client: AsyncClient):
    resp = await admin_client.post(f"/api/v1/workflow/{uuid.uuid4()}/approve", json={})
    assert resp.status_code == 404

@pytest.mark.asyncio
async def test_approve_already_approved(admin_client: AsyncClient, db_session, viewer_user):
    doc = DocumentFactory.build(uploaded_by=viewer_user.id, status=DocumentStatusEnum.approved)
    db_session.add(doc)
    await db_session.commit()
    await db_session.refresh(doc)

    resp = await admin_client.post(f"/api/v1/workflow/{doc.id}/approve", json={})
    assert resp.status_code == 400
