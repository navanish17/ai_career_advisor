from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ai_career_advisor.core.database import get_db
from ai_career_advisor.services.career_service import CareerService
from ai_career_advisor.Schemas.career import CareerResponse


router = APIRouter(tags=["Careers"])


@router.get(
    "/from-branch/{branch_id}",
    response_model=List[CareerResponse]
)
async def get_careers_from_branch(
    branch_id: int,
    db: AsyncSession = Depends(get_db)
):
    careers = await CareerService.get_careers_by_branch(branch_id, db)

    if not careers:
        raise HTTPException(
            status_code=404,
            detail="No careers found for this branch"
        )

    return careers
