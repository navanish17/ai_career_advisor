from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ai_career_advisor.Schemas.roadmap import RoadmapGenerateRequest
from ai_career_advisor.services.roadmap_service import RoadmapService
from ai_career_advisor.core.database import get_db
from ai_career_advisor.core.security import get_current_user

router = APIRouter(prefix="/roadmap", tags=["Roadmap"])


@router.post("/generate")
async def generate_roadmap(
    payload: RoadmapGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        roadmap_id = await RoadmapService.create_guided_roadmap(
            db=db,
            user_id=current_user.id,
            degree_id=payload.degree_id,
            branch_id=payload.branch_id,
            career_id=payload.career_id
        )
        return {
            "message": "Roadmap generated successfully",
            "roadmap_id": roadmap_id
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/{roadmap_id}")
async def get_roadmap(
    roadmap_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        return await RoadmapService.get_roadmap(
            db=db,
            user_id=current_user.id,
            roadmap_id=roadmap_id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

