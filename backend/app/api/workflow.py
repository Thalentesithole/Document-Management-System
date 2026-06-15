from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.user import User, RoleEnum
from app.api.deps import get_current_user, require_roles
from app.agents.workflow_agent import WorkflowAgent
from app.services.audit import AuditService
from pydantic import BaseModel
import uuid

router = APIRouter()

class ActionRequest(BaseModel):
    comments: str = ""

@router.post("/{id}/approve")
async def approve_document(
    id: uuid.UUID,
    payload: ActionRequest,
    current_user: User = Depends(require_roles([RoleEnum.admin, RoleEnum.reviewer, RoleEnum.manager])),
    db: AsyncSession = Depends(get_db)
):
    try:
        document = await WorkflowAgent.process_action(db, id, current_user.id, "approve", payload.comments)
        
        await AuditService.log_action(
            db=db,
            action="workflow_approve",
            entity_type="Document",
            entity_id=str(id),
            user_id=current_user.id,
            user_email=current_user.email,
            user_role=current_user.role.value,
            new_value={"comments": payload.comments, "new_status": document.status.value}
        )
        
        return {"message": "Document approved", "status": document.status}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{id}/reject")
async def reject_document(
    id: uuid.UUID,
    payload: ActionRequest,
    current_user: User = Depends(require_roles([RoleEnum.admin, RoleEnum.manager])),
    db: AsyncSession = Depends(get_db)
):
    try:
        document = await WorkflowAgent.process_action(db, id, current_user.id, "reject", payload.comments)
        
        await AuditService.log_action(
            db=db,
            action="workflow_reject",
            entity_type="Document",
            entity_id=str(id),
            user_id=current_user.id,
            user_email=current_user.email,
            user_role=current_user.role.value,
            new_value={"comments": payload.comments, "new_status": document.status.value}
        )
        
        return {"message": "Document rejected", "status": document.status}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{id}/return")
async def return_document(
    id: uuid.UUID,
    payload: ActionRequest,
    current_user: User = Depends(require_roles([RoleEnum.admin, RoleEnum.manager])),
    db: AsyncSession = Depends(get_db)
):
    """Return a document to Reviewer (Manager action at Stage 2)."""
    try:
        document = await WorkflowAgent.process_action(db, id, current_user.id, "return", payload.comments)
        
        await AuditService.log_action(
            db=db,
            action="workflow_return",
            entity_type="Document",
            entity_id=str(id),
            user_id=current_user.id,
            user_email=current_user.email,
            user_role=current_user.role.value,
            new_value={"comments": payload.comments, "new_status": document.status.value}
        )
        
        return {"message": "Document returned to reviewer", "status": document.status}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{id}/history")
async def get_workflow_history(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import select
    from app.models.approval_workflow import ApprovalWorkflow
    from app.models.user import User
    
    result = await db.execute(
        select(ApprovalWorkflow, User.full_name, User.role)
        .join(User, ApprovalWorkflow.approver_id == User.id)
        .where(ApprovalWorkflow.document_id == id)
        .order_by(ApprovalWorkflow.approved_at.asc())
    )
    
    history = []
    for row in result.all():
        history.append({
            "id": row[0].id,
            "stage_number": row[0].stage_number,
            "action": row[0].action,
            "comments": row[0].comments,
            "approved_at": row[0].approved_at,
            "approver_name": row[1],
            "approver_role": row[2]
        })
    return history
