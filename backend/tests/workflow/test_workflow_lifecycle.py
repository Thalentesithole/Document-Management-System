import pytest
from httpx import AsyncClient
from tests.fixtures.factories import DocumentFactory
from app.models.document import DocumentStatusEnum

@pytest.mark.asyncio
async def test_full_3_stage_approval(admin_client: AsyncClient, reviewer_client: AsyncClient, manager_client: AsyncClient, db_session, viewer_user):
    doc = DocumentFactory.build(uploaded_by=viewer_user.id, status=DocumentStatusEnum.pending_review)
    db_session.add(doc)
    await db_session.commit()
    await db_session.refresh(doc)

    # Stage 1: Reviewer
    resp1 = await reviewer_client.post(f"/api/v1/workflow/{doc.id}/approve", json={"comments": "stage 1"})
    assert resp1.status_code == 200
    assert resp1.json()["status"] == DocumentStatusEnum.pending_manager_approval

    # Stage 2: Manager
    resp2 = await manager_client.post(f"/api/v1/workflow/{doc.id}/approve", json={"comments": "stage 2"})
    assert resp2.status_code == 200
    assert resp2.json()["status"] == DocumentStatusEnum.pending_finance_approval

    # Stage 3: Admin (Finance)
    resp3 = await admin_client.post(f"/api/v1/workflow/{doc.id}/approve", json={"comments": "stage 3"})
    assert resp3.status_code == 200
    assert resp3.json()["status"] == DocumentStatusEnum.approved

@pytest.mark.asyncio
async def test_reject_at_stage_2(admin_client: AsyncClient, reviewer_client: AsyncClient, manager_client: AsyncClient, db_session, viewer_user):
    doc = DocumentFactory.build(uploaded_by=viewer_user.id, status=DocumentStatusEnum.pending_review)
    db_session.add(doc)
    await db_session.commit()
    await db_session.refresh(doc)

    resp1 = await reviewer_client.post(f"/api/v1/workflow/{doc.id}/approve", json={})
    assert resp1.status_code == 200

    resp2 = await manager_client.post(f"/api/v1/workflow/{doc.id}/reject", json={"comments": "No budget"})
    assert resp2.status_code == 200
    assert resp2.json()["status"] == DocumentStatusEnum.rejected

@pytest.mark.asyncio
async def test_duplicate_flagged_can_be_approved(reviewer_client: AsyncClient, db_session, viewer_user):
    doc = DocumentFactory.build(uploaded_by=viewer_user.id, status=DocumentStatusEnum.duplicate_flagged)
    db_session.add(doc)
    await db_session.commit()
    await db_session.refresh(doc)

    resp = await reviewer_client.post(f"/api/v1/workflow/{doc.id}/approve", json={"comments": "Not actually a duplicate"})
    assert resp.status_code == 200
    assert resp.json()["status"] == DocumentStatusEnum.pending_manager_approval
