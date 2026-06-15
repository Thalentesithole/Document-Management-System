import pytest
from unittest.mock import patch, MagicMock
from app.tasks.extraction import extract_invoice_data_async
from app.agents.insights_agent import InsightsAgent
from tests.fixtures.factories import DocumentFactory
from app.models.document import DocumentStatusEnum

@pytest.mark.asyncio
@patch("app.tasks.extraction.genai.Client")
@patch("app.tasks.extraction.httpx.AsyncClient.get")
@patch("app.tasks.extraction.check_duplicates_task.delay")
async def test_extraction_parses_valid_json_response(mock_dup, mock_get, mock_genai, db_session):
    doc = DocumentFactory.build(status=DocumentStatusEnum.pending_extraction)
    db_session.add(doc)
    await db_session.commit()
    await db_session.refresh(doc)

    mock_get.return_value = MagicMock(content=b"dummy")
    
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"Vendor Name": "Test Vendor", "Total Amount": 123.45}'
    mock_client.models.generate_content.return_value = mock_response
    mock_genai.return_value = mock_client

    await extract_invoice_data_async(str(doc.id))

    await db_session.refresh(doc)
    assert doc.vendor_name == "Test Vendor"
    assert float(doc.total_amount) == 123.45
    assert doc.status == DocumentStatusEnum.pending_review
    mock_dup.assert_called_once()

@pytest.mark.asyncio
@patch("app.tasks.extraction.genai.Client")
@patch("app.tasks.extraction.httpx.AsyncClient.get")
async def test_extraction_invalid_json_rejects_document(mock_get, mock_genai, db_session):
    doc = DocumentFactory.build(status=DocumentStatusEnum.pending_extraction)
    db_session.add(doc)
    await db_session.commit()
    await db_session.refresh(doc)

    mock_get.return_value = MagicMock(content=b"dummy")
    
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = 'this is not json'
    mock_client.models.generate_content.return_value = mock_response
    mock_genai.return_value = mock_client

    await extract_invoice_data_async(str(doc.id))

    await db_session.refresh(doc)
    assert doc.status == DocumentStatusEnum.rejected

@pytest.mark.asyncio
@patch("app.agents.insights_agent.genai.Client")
async def test_insights_parses_valid_response(mock_genai):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"trends": "up"}'
    mock_client.models.generate_content.return_value = mock_response
    mock_genai.return_value = mock_client

    res = await InsightsAgent.generate_insights([{"vendor": "A", "total_spend": 100}])
    assert res == {"trends": "up"}
