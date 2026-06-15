from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.user import User, RoleEnum
from app.api.deps import get_current_user, require_roles
from app.agents.reporting_agent import ReportingAgent
from app.agents.insights_agent import InsightsAgent

router = APIRouter()

@router.get("/")
async def get_insights(
    current_user: User = Depends(require_roles([RoleEnum.admin, RoleEnum.manager, RoleEnum.viewer])),
    db: AsyncSession = Depends(get_db)
):
    spend_data = await ReportingAgent.get_spend_summary(db)
    insights = await InsightsAgent.generate_insights(spend_data.get("spend_summary", []))
    if "error" in insights:
        raise HTTPException(status_code=500, detail=insights["error"])
    return insights
