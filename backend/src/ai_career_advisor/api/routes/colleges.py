from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ai_career_advisor.core.database import get_db
from ai_career_advisor.services.college_service import CollegeService
from ai_career_advisor.Schemas.college import CollegeListResponse


router = APIRouter(prefix="/colleges", tags=["Colleges"])


@router.get("", response_model=CollegeListResponse)
async def list_colleges(
    state: str = Query(..., description="State name"),
    db: AsyncSession = Depends(get_db)
):
    colleges = await CollegeService.get_colleges_by_state(db, state)

    return {
        "count": len(colleges),
        "colleges": colleges
    }
