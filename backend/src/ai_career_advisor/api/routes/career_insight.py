from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ai_career_advisor.core.database import get_db
from ai_career_advisor.Schemas.career_insight import CareerInsightResponse
from ai_career_advisor.services.career_insight_service import CareerInsightService
from ai_career_advisor.services.career_service import CareerService  
from ai_career_advisor.core.logger import logger  

router = APIRouter(prefix="/api/career-insight", tags=["Career Insight"])


def normalize_projects(projects):
    """Normalize projects to required format"""
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
    """
    Get Top 1% career insight with lazy loading:
    1. Check cache (database)
    2. If not found, generate using LLM
    3. Save and return
    """
    
    
    logger.info(f" Fetching insight for career_id: {career_id}")
    insight = await CareerInsightService.get_by_career_id(career_id, db)
    
    
    if not insight:
        logger.warning(f" Insight not found in DB for career_id: {career_id}")
        
        
        career = await CareerService.get_career_by_id(career_id, db)
        if not career:
            raise HTTPException(
                status_code=404,
                detail=f"Career with ID {career_id} not found"
            )
        
        logger.info(f" Generating insight using LLM for: {career.name}")
        
        try:
            #
            insight = await CareerInsightService.generate_and_save(
                career_id=career_id,
                career_name=career.name,
                db=db
            )
        except Exception as e:
            logger.error(f" Failed to generate insight: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate career insight: {str(e)}"
            )
    
   
    logger.success(f" Returning insight for career_id: {career_id}")
    
    return CareerInsightResponse(
    career_id=insight.career_id,
    skills=insight.skills,
    internships=insight.internships,
    projects=normalize_projects(insight.projects),
    programs=insight.programs,
    top_salary=insight.top_salary  
)
