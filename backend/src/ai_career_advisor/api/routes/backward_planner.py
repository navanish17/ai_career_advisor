from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ai_career_advisor.core.database import get_db
from ai_career_advisor.core.logger import logger
from ai_career_advisor.Schemas.backward_planner import (
    BackwardPlannerRequest,
    BackwardPlannerSuccessResponse,
    BackwardPlannerErrorResponse,
    BackwardRoadmapResponse
)
from ai_career_advisor.services.career_normalizer import CareerNormalizerService
from ai_career_advisor.services.backward_roadmap_service import BackwardRoadmapService
from ai_career_advisor.services.career_template_service import CareerTemplateService
from ai_career_advisor.services.backward_planner_llm import BackwardPlannerLLM


router = APIRouter(prefix="/backward-planner", tags=["Backward Planner"])


@router.post("/generate", response_model=BackwardPlannerSuccessResponse)
async def generate_backward_roadmap(
    payload: BackwardPlannerRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate backward career roadmap from career goal
    
    Flow:
    1. Normalize & validate career input
    2. Check cache (existing roadmap)
    3. Check template (pre-built roadmap)
    4. Generate with LLM (if no cache/template)
    5. Save to database
    6. Return roadmap
    
    Examples:
        Input: "software engineer"
        Input: "doctor"
        Input: "IAS officer"
    """
    
    logger.info(f"\n{'='*60}")
    logger.info(f"🎯 BACKWARD PLANNER REQUEST: '{payload.career_goal}'")
    logger.info(f"{'='*60}")
    
    # =============================
    # STEP 1: NORMALIZE & VALIDATE
    # =============================
    normalized = await CareerNormalizerService.normalize_and_validate(
        payload.career_goal
    )
    
    if not normalized["is_valid"]:
        logger.warning(f"   ❌ Invalid career goal rejected")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid career goal",
                "message": normalized.get("reason"),
                "suggestion": "Please provide a specific career (e.g., Doctor, Engineer, Teacher, CA, IAS Officer)"
            }
        )
    
    career_name = normalized["normalized_career"]
    category = normalized.get("category")
    
    # =============================
    # STEP 2: CHECK CACHE
    # =============================
    logger.info(f"🔍 Checking cache for '{career_name}'...")
    
    cached_roadmap = await BackwardRoadmapService.get_by_career(
        db,
        career_name=career_name
    )
    
    if cached_roadmap:
        logger.success(f"   💾 Found in cache! (ID: {cached_roadmap.id})")
        return BackwardPlannerSuccessResponse(
            success=True,
            source="cache",
            roadmap=BackwardRoadmapResponse(**cached_roadmap.to_dict())
        )
    
    # =============================
    # STEP 3: CHECK TEMPLATE
    # =============================
    logger.info(f"📋 Checking templates for '{career_name}'...")
    
    template = await CareerTemplateService.get_by_name(
        db,
        career_name=career_name
    )
    
    if template:
        logger.success(f"   📋 Template found! Using pre-built roadmap")
        
        # Create roadmap from template
        roadmap = await BackwardRoadmapService.create_from_template(
            db,
            career_goal_input=payload.career_goal,
            normalized_career=career_name,
            category=category,
            template_data=template.to_dict(),
            user_id=None  # Can be added later for user-specific roadmaps
        )
        
        return BackwardPlannerSuccessResponse(
            success=True,
            source="template",
            roadmap=BackwardRoadmapResponse(**roadmap.to_dict())
        )
    
    # =============================
    # STEP 4: GENERATE WITH LLM
    # =============================
    logger.info(f"🤖 No cache/template found. Generating with AI...")
    
    generated = await BackwardPlannerLLM.generate_roadmap(
        career_name=career_name,
        category=category
    )
    
    # Handle generation errors
    if "error" in generated:
        error_type = generated.get("error")
        error_message = generated.get("message", "Failed to generate roadmap")
        
        logger.error(f"   ❌ Generation failed: {error_type}")
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Roadmap generation failed",
                "message": error_message,
                "error_type": error_type
            }
        )
    
    # =============================
    # STEP 5: SAVE TO DATABASE
    # =============================
    roadmap = await BackwardRoadmapService.create_from_llm(
        db,
        career_goal_input=payload.career_goal,
        normalized_career=career_name,
        category=category,
        roadmap_data=generated,
        user_id=None
    )
    
    logger.success(f"\n{'='*60}")
    logger.success(f"✅ ROADMAP SUCCESSFULLY GENERATED FOR '{career_name}'")
    logger.success(f"{'='*60}\n")
    
    return BackwardPlannerSuccessResponse(
        success=True,
        source="llm_generated",
        roadmap=BackwardRoadmapResponse(**roadmap.to_dict())
    )


@router.get("/templates", response_model=list[str])
async def get_available_templates(db: AsyncSession = Depends(get_db)):
    """
    Get list of available pre-built career templates
    
    Returns:
        List of career names with templates
    """
    templates = await CareerTemplateService.get_all_active(db)
    return [template.career_name for template in templates]
