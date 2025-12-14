from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ai_career_advisor.core.database import get_db
from ai_career_advisor.services.branch_service import BranchService
from ai_career_advisor.Schemas.branch import BranchResponse
from ai_career_advisor.core.logger import logger

router = APIRouter(
    prefix="/api/branch",
    tags=["Branch"]
)


@router.get(
    "/from-degree/{degree_id}",
    response_model=list[BranchResponse]
)
async def get_branches_from_degree(
    degree_id: int,
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"API called: get branches for degree_id={degree_id}")

    branches = await BranchService.get_branches_by_degree(db, degree_id)

    if not branches:
        raise HTTPException(
            status_code=404,
            detail="No branches found for this degree"
        )

    return branches
