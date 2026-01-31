from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ai_career_advisor.core.database import get_db
from ai_career_advisor.services.career_service import CareerService
from ai_career_advisor.services.career_llm import generate_career_details
from ai_career_advisor.Schemas.career import CareerResponse
from ai_career_advisor.core.logger import logger
from ai_career_advisor.models.career import Career
from sqlalchemy import select

router = APIRouter(prefix="/api/career", tags=["Careers"])

@router.get(
    "/from-branch/{branch_id}",
    response_model=List[CareerResponse]
)
async def get_careers_from_branch(
    branch_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all careers for a branch (without full details)"""
    careers = await CareerService.get_careers_by_branch(branch_id, db)
    
    if not careers:
        raise HTTPException(
            status_code=404,
            detail="No careers found for this branch"
        )
    
    return careers


@router.get(
    "/{career_id}/details",
    response_model=CareerResponse
)
async def get_career_details(
    career_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get career details with lazy loading:
    - If details exist in DB → Return from cache
    - If null → Generate using LLM → Save → Return
    """
    

    result = await db.execute(
        select(Career).where(Career.id == career_id)
    )
    career = result.scalar_one_or_none()
    
    if not career:
        raise HTTPException(status_code=404, detail="Career not found")
    
    
    if career.description and career.market_trend and career.salary_range:
        logger.info(f"Serving cached data for: {career.name}")
        return career
    
    logger.info(f" Generating LLM data for: {career.name}")
    
    try:
        
        llm_data = generate_career_details(career.name)
        
        
        career.description = llm_data.get("description")
        career.market_trend = llm_data.get("market_trend")
        career.salary_range = llm_data.get("salary_range")
        
        db.add(career)
        await db.commit()
        await db.refresh(career)
        
        logger.success(f" Generated & cached data for: {career.name}")
        return career
        
    except Exception as e:
        logger.error(f" LLM generation failed for {career.name}: {e}")
        
        
        career.description = f"{career.name} is a professional role in the industry."
        career.market_trend = "Growing demand in India"
        career.salary_range = "3 LPA to 8 LPA"
        
        return career
