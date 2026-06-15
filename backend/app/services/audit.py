from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog
from typing import Any, Optional
import uuid

class AuditService:
    @staticmethod
    async def log_action(
        db: AsyncSession,
        action: str,
        entity_type: str,
        entity_id: str,
        user_id: Optional[uuid.UUID] = None,
        user_email: Optional[str] = None,
        user_role: Optional[str] = None,
        old_value: Optional[dict[str, Any]] = None,
        new_value: Optional[dict[str, Any]] = None
    ) -> AuditLog:
        audit_log = AuditLog(
            user_id=user_id,
            user_email=user_email,
            user_role=user_role,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=old_value,
            new_value=new_value
        )
        db.add(audit_log)
        await db.commit()
        await db.refresh(audit_log)
        return audit_log
