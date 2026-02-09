from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ai_career_advisor.core.database import get_db
from ai_career_advisor.Schemas.career_insight import CareerInsightResponse
from ai_career_advisor.services.career_insight_service import CareerInsightService
from ai_career_advisor.services.career_service import CareerService  
from ai_career_advisor.models.career_insight import CareerInsight  # For fallback data
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
        
        
        # Store career name BEFORE try block to avoid detached object access after rollback
        career_name = career.name
        logger.info(f"🔄 Generating insight using LLM for: {career_name}")
        
        try:
            # Try to generate using LLM
            insight = await CareerInsightService.generate_and_save(
                career_id=career_id,
                career_name=career_name,
                db=db
            )
        except Exception as e:
            
            logger.error(f"⚠️ Failed to generate insight: {e}")
            logger.info(f"📝 Creating fallback insight for: {career_name}")
            
            # Rollback any failed transaction
            await db.rollback()
            
            # Check again if insight was created during the failed attempt
            check_result = await db.execute(
                select(CareerInsight).where(CareerInsight.career_id == career_id)
            )
            existing_insight = check_result.scalar_one_or_none()
            
            if existing_insight:
                logger.info(f"✅ Found existing insight after rollback for: {career_name}")
                insight = existing_insight
            else:
                # Create fallback insight data
                try:
                    fallback_insight = CareerInsight(
                        career_id=career_id,
                        skills=[
                            "Strong technical foundation",
                            "Problem-solving abilities",
                            "Communication skills",
                            "Team collaboration",
                            "Continuous learning mindset",
                            "Industry-specific expertise",
                            "Project management",
                            "Analytical thinking"
                        ],
                        internships=[
                            "Top companies in the field",
                            "Startups with growth potential",
                            "Research institutions"
                        ],
                        projects={
                            "production": [
                                f"Build a real-world {career_name} project",
                                "Contribute to open-source projects"
                            ],
                            "research": [
                                f"Research paper on {career_name} trends"
                            ]
                        },
                        programs=[
                            "Professional certifications",
                            "Industry workshops and conferences"
                        ],
                        top_salary=f"₹15-50 LPA in India (Top 1% professionals)",
                        is_active=True
                    )
                    
                    db.add(fallback_insight)
                    await db.commit()
                    await db.refresh(fallback_insight)
                    
                    insight = fallback_insight
                    logger.info(f"✅ Fallback insight created for: {career_name}")
                except Exception as fallback_error:
                    logger.error(f"❌ Failed to create fallback insight: {fallback_error}")
                    await db.rollback()
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to generate or create fallback insight: {str(fallback_error)}"
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
