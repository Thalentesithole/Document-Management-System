from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.user import User, RoleEnum
from app.models.audit_log import AuditLog
from app.api.deps import require_roles

router = APIRouter()

@router.get("/")
async def get_audit_logs(
    skip: int = 0, 
    limit: int = 100,
    current_user: User = Depends(require_roles([RoleEnum.admin])),
    db: AsyncSession = Depends(get_db)
):
    query = select(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    logs = result.scalars().all()
    return logs
