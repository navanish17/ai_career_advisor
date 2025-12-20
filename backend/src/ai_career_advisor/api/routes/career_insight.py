from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ai_career_advisor.core.database import get_db
from ai_career_advisor.Schemas.career_insight import CareerInsightResponse
from ai_career_advisor.services.career_insight_service import CareerInsightService

router = APIRouter(prefix="/api/career-insight", tags=["Career Insight"])

def normalize_projects(projects):
    if isinstance(projects, dict):
        return {
            "production": projects.get("production", []),
            "research": projects.get("research", [])
        }

    if isinstance(projects, list):
        return {
            "production": projects[:2],
            "research": projects[2:3] if len(projects) > 2 else []
        }

    return {
        "production": [],
        "research": []
    }



@router.get(
    "/{career_id}",
    response_model=CareerInsightResponse
)
async def get_career_insight(
    career_id: int,
    db: AsyncSession = Depends(get_db)
):
    insight = await CareerInsightService.get_by_career_id(career_id, db)

    if not insight:
        raise HTTPException(
            status_code=404,
            detail="Top 1% career insight not found"
        )

    return CareerInsightResponse(
    career_id=insight.career_id,
    skills=insight.skills,
    internships=insight.internships,
    projects=normalize_projects(insight.projects),
    programs=insight.programs
)
