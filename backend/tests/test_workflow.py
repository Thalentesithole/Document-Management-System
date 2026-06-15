import pytest
from app.agents.workflow_agent import WorkflowAgent
from app.models.document import Document, DocumentStatusEnum
import uuid
from fastapi import HTTPException

@pytest.mark.asyncio
async def test_workflow_agent_approve_from_review(db_session, test_user):
    uploader_id = uuid.uuid4()
    doc = Document(
        file_name="test.pdf",
        file_url="http://test.pdf",
        file_hash="hash1",
        status=DocumentStatusEnum.pending_review,
        uploaded_by=uploader_id
    )
    db_session.add(doc)
    await db_session.commit()
    await db_session.refresh(doc)
    
    approved_doc = await WorkflowAgent.process_action(db_session, doc.id, test_user.id, "approve", "Looks good")
    
    assert approved_doc.status == DocumentStatusEnum.pending_manager_approval

@pytest.mark.asyncio
async def test_workflow_agent_reject(db_session, test_user):
    uploader_id = uuid.uuid4()
    doc = Document(
        file_name="test.pdf",
        file_url="http://test.pdf",
        file_hash="hash2",
        status=DocumentStatusEnum.pending_finance_approval,
        uploaded_by=uploader_id
    )
    db_session.add(doc)
    await db_session.commit()
    await db_session.refresh(doc)
    
    rejected_doc = await WorkflowAgent.process_action(db_session, doc.id, test_user.id, "reject", "Missing details")
    
    assert rejected_doc.status == DocumentStatusEnum.rejected

@pytest.mark.asyncio
async def test_workflow_prevent_self_approval(db_session, test_user):
    doc = Document(
        file_name="test.pdf",
        file_url="http://test.pdf",
        file_hash="hash3",
        status=DocumentStatusEnum.pending_review,
        uploaded_by=test_user.id
    )
    db_session.add(doc)
    await db_session.commit()
    await db_session.refresh(doc)
    
    with pytest.raises(HTTPException) as excinfo:
        await WorkflowAgent.process_action(db_session, doc.id, test_user.id, "approve", "Looks good")
    assert excinfo.value.status_code == 403
