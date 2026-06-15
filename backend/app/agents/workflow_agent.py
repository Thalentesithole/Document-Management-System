from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.document import Document, DocumentStatusEnum
from app.models.approval_workflow import ApprovalWorkflow
from app.models.user import User, RoleEnum
from app.services.audit import AuditService
from fastapi import HTTPException
import uuid

class WorkflowAgent:
    """
    2-Step Approval Workflow:
      Stage 1 — Reviewer:  pending_review / duplicate_flagged / returned_to_reviewer
      Stage 2 — Manager:   pending_manager_approval
    """

    # Stage definitions: (allowed statuses, allowed roles, stage number)
    STAGE_1_STATUSES = {
        DocumentStatusEnum.pending_review,
        DocumentStatusEnum.duplicate_flagged,
        DocumentStatusEnum.returned_to_reviewer,
    }
    STAGE_2_STATUSES = {
        DocumentStatusEnum.pending_manager_approval,
    }

    STAGE_1_ROLES = {RoleEnum.reviewer, RoleEnum.admin}
    STAGE_2_ROLES = {RoleEnum.manager, RoleEnum.admin}

    @staticmethod
    async def process_action(
        db: AsyncSession,
        document_id: uuid.UUID,
        user_id: uuid.UUID,
        action: str,
        comments: str = ""
    ):
        # --- Fetch document ---
        result = await db.execute(select(Document).where(Document.id == document_id))
        document = result.scalar_one_or_none()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # --- Fetch user ---
        user_res = await db.execute(select(User).where(User.id == user_id))
        user = user_res.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # --- Self-approval guard ---
        if document.uploaded_by == user_id:
            raise HTTPException(status_code=403, detail="Cannot approve your own submission")

        # --- Validate action ---
        valid_actions = {"approve", "reject", "return"}
        if action not in valid_actions:
            raise HTTPException(status_code=400, detail=f"Invalid action. Must be one of: {', '.join(valid_actions)}")

        old_status = document.status
        stage_number = 0

        # ===== STAGE 1: Reviewer =====
        if document.status in WorkflowAgent.STAGE_1_STATUSES:
            if user.role not in WorkflowAgent.STAGE_1_ROLES:
                raise HTTPException(
                    status_code=403,
                    detail="Only Reviewers or Admins can perform Stage 1 review."
                )
            if action == "return":
                raise HTTPException(
                    status_code=400,
                    detail="Return action is only available at Stage 2 (Manager)."
                )
            stage_number = 1
            if action == "approve":
                document.status = DocumentStatusEnum.pending_manager_approval
            else:
                document.status = DocumentStatusEnum.rejected

        # ===== STAGE 2: Manager =====
        elif document.status in WorkflowAgent.STAGE_2_STATUSES:
            if user.role not in WorkflowAgent.STAGE_2_ROLES:
                raise HTTPException(
                    status_code=403,
                    detail="Only Managers or Admins can perform Stage 2 approval."
                )
            stage_number = 2
            if action == "approve":
                document.status = DocumentStatusEnum.approved
            elif action == "return":
                document.status = DocumentStatusEnum.returned_to_reviewer
            else:
                document.status = DocumentStatusEnum.rejected

            else:
                document.status = DocumentStatusEnum.rejected

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot process document in current status: {document.status}"
            )

        # --- Record workflow entry ---
        workflow_entry = ApprovalWorkflow(
            document_id=document.id,
            stage_number=stage_number,
            approver_id=user_id,
            action=action,
            comments=comments
        )
        db.add(workflow_entry)

        # --- Audit log ---
        await AuditService.log_action(
            db=db,
            action=f"workflow_{action}",
            entity_type="Document",
            entity_id=str(document.id),
            user_id=user_id,
            old_value={"status": old_status.value if hasattr(old_status, 'value') else str(old_status)},
            new_value={
                "status": document.status.value if hasattr(document.status, 'value') else str(document.status),
                "stage": stage_number,
                "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
                "comments": comments
            }
        )

        await db.commit()
        return document
