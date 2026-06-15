import pytest
from httpx import AsyncClient
from unittest.mock import patch
from tests.fixtures.factories import DocumentFactory
from app.models.document import DocumentStatusEnum

@pytest.mark.asyncio
async def test_spend_summary_admin_access(admin_client: AsyncClient, db_session):
    doc = DocumentFactory.build(status=DocumentStatusEnum.approved, total_amount=100.0, vendor_name="Vendor A")
    db_session.add(doc)
    await db_session.commit()

    resp = await admin_client.get("/api/v1/reports/spend-summary")
    assert resp.status_code == 200
    assert "spend_summary" in resp.json()

@pytest.mark.asyncio
async def test_spend_summary_viewer_forbidden(viewer_client: AsyncClient):
    resp = await viewer_client.get("/api/v1/reports/spend-summary")
    assert resp.status_code == 403

@pytest.mark.asyncio
async def test_spend_summary_manager_access(manager_client: AsyncClient):
    resp = await manager_client.get("/api/v1/reports/spend-summary")
    assert resp.status_code == 200

@pytest.mark.asyncio
@patch("app.api.insights.InsightsAgent.generate_insights")
async def test_insights_endpoint_with_mock(mock_gen, admin_client: AsyncClient):
    mock_gen.return_value = {"insights": "Some insights"}
    resp = await admin_client.get("/api/v1/insights/")
    assert resp.status_code == 200
    assert resp.json() == {"insights": "Some insights"}

@pytest.mark.asyncio
async def test_insights_viewer_forbidden(viewer_client: AsyncClient):
    resp = await viewer_client.get("/api/v1/insights/")
    assert resp.status_code == 403
