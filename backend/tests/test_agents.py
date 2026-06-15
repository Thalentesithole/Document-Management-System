import pytest
from app.agents.reporting_agent import ReportingAgent
from app.models.document import Document, DocumentStatusEnum

@pytest.mark.asyncio
async def test_reporting_agent_spend_summary(db_session):
    doc1 = Document(
        file_name="t1.pdf", file_url="u1", file_hash="h1",
        vendor_name="Vendor A", total_amount=100.0, status=DocumentStatusEnum.approved
    )
    doc2 = Document(
        file_name="t2.pdf", file_url="u2", file_hash="h2",
        vendor_name="Vendor A", total_amount=50.0, status=DocumentStatusEnum.approved
    )
    doc3 = Document(
        file_name="t3.pdf", file_url="u3", file_hash="h3",
        vendor_name="Vendor B", total_amount=200.0, status=DocumentStatusEnum.approved
    )
    doc4 = Document(
        file_name="t4.pdf", file_url="u4", file_hash="h4",
        vendor_name="Vendor A", total_amount=100.0, status=DocumentStatusEnum.rejected # Should be ignored
    )
    db_session.add_all([doc1, doc2, doc3, doc4])
    await db_session.commit()
    
    report = await ReportingAgent.get_spend_summary(db_session)
    summary = report["spend_summary"]
    
    assert len(summary) == 2
    for item in summary:
        if item["vendor"] == "Vendor A":
            assert item["total_spend"] == 150.0
        if item["vendor"] == "Vendor B":
            assert item["total_spend"] == 200.0
