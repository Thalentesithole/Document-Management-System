import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.audit import AuditService
from app.models.audit_log import AuditLog
from sqlalchemy import select

@pytest.mark.asyncio
async def test_log_action_creates_record(db_session: AsyncSession):
    user_id = uuid.uuid4()
    entity_id = str(uuid.uuid4())
    log = await AuditService.log_action(
        db=db_session,
        action="upload",
        entity_type="Document",
        entity_id=entity_id,
        user_id=user_id,
        old_value={"status": "new"},
        new_value={"status": "pending"}
    )
    assert log.id is not None
    assert log.action == "upload"
    assert log.entity_type == "Document"
    assert log.entity_id == entity_id
    assert log.user_id == user_id
    assert log.old_value == {"status": "new"}
    assert log.new_value == {"status": "pending"}

@pytest.mark.asyncio
async def test_log_action_without_user(db_session: AsyncSession):
    entity_id = str(uuid.uuid4())
    log = await AuditService.log_action(
        db=db_session,
        action="system_task",
        entity_type="System",
        entity_id=entity_id
    )
    assert log.id is not None
    assert log.user_id is None
