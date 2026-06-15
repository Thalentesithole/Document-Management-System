from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.user import User, RoleEnum
from app.api.deps import get_current_user, require_roles
from app.agents.reporting_agent import ReportingAgent
from typing import Optional

router = APIRouter()

# Allow admins, approvers, and viewers to see reports
REPORT_ROLES = [RoleEnum.admin, RoleEnum.manager, RoleEnum.viewer]

@router.get("/spend-summary")
async def spend_summary(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    vendor_name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(require_roles(REPORT_ROLES)),
    db: AsyncSession = Depends(get_db)
):
    return await ReportingAgent.get_spend_summary(db, start_date, end_date, vendor_name, status)

@router.get("/vendor-analysis")
async def vendor_analysis(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    vendor_name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(require_roles(REPORT_ROLES)),
    db: AsyncSession = Depends(get_db)
):
    return await ReportingAgent.get_vendor_analysis(db, start_date, end_date, vendor_name, status)

@router.get("/approval-status")
async def approval_status(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    vendor_name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(require_roles(REPORT_ROLES)),
    db: AsyncSession = Depends(get_db)
):
    return await ReportingAgent.get_approval_status(db, start_date, end_date, vendor_name, status)

@router.get("/tax-vat")
async def tax_vat(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    vendor_name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(require_roles(REPORT_ROLES)),
    db: AsyncSession = Depends(get_db)
):
    return await ReportingAgent.get_tax_report(db, start_date, end_date, vendor_name, status)
