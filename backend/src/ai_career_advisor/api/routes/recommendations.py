"""
Recommendation System API Routes
Endpoints for career recommendations, quiz, and interaction tracking
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ai_career_advisor.core.database import get_db
from ai_career_advisor.core.logger import logger
from ai_career_advisor.services.recommendation_service import RecommendationService
from ai_career_advisor.Schemas.recommendations import (
    QuizSubmitRequest,
    UserPreferencesResponse,
    RecommendationsResponse,
    CareerRecommendation,
    SimilarCareersResponse,
    InteractionTrackRequest,
    InteractionResponse,
    RecommendationFeedbackRequest,
    FeedbackResponse
)
from typing import Optional


router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


# ================== QUIZ ENDPOINTS ==================

@router.post("/quiz", response_model=UserPreferencesResponse)
async def submit_quiz(
    request: QuizSubmitRequest,
    user_email: str,  # In production, get from auth token
    db: AsyncSession = Depends(get_db)
):
    """
    Submit career quiz answers to build user profile.
    
    This creates/updates user preferences used for recommendations.
    """
    try:
        logger.info(f"📝 Quiz submission from: {user_email}")
        
        preferences = request.model_dump(exclude_unset=True)
        
        result = await RecommendationService.save_user_preferences(
            db=db,
            user_email=user_email,
            preferences=preferences
        )
        
        return UserPreferencesResponse(
            id=result.id,
            user_email=result.user_email,
            skills=result.skills or [],
            interests=result.interests or [],
            education_level=result.education_level,
            current_stream=result.current_stream,
            preferred_work_style=result.preferred_work_style,
            preferred_salary_range=result.preferred_salary_range,
            quiz_completed=result.quiz_completed,
            quiz_completion_percentage=result.quiz_completion_percentage
        )
        
    except Exception as e:
        logger.error(f"Quiz submission error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving quiz: {str(e)}")


# ================== RECOMMENDATION ENDPOINTS ==================

@router.get("/careers", response_model=RecommendationsResponse)
async def get_career_recommendations(
    user_email: str,  # In production, get from auth token
    top_k: int = 5,
    db: AsyncSession = Depends(get_db)
):
    """
    Get personalized career recommendations for a user.
    
    Returns top-K careers ranked by match score.
    
    - **user_email**: User identifier
    - **top_k**: Number of recommendations (default: 5, max: 10)
    """
    try:
        if top_k > 10:
            top_k = 10  # Cap at 10
        
        logger.info(f"🎯 Getting recommendations for: {user_email}")
        
        results = await RecommendationService.get_recommendations(
            db=db,
            user_email=user_email,
            top_k=top_k
        )
        
        recommendations = []
        for r in results:
            career = r["career"]
            recommendations.append(CareerRecommendation(
                career_name=career["career_name"],
                career_category=career.get("career_category"),
                short_description=career.get("short_description"),
                match_score=r["match_score"],
                content_score=r.get("content_score"),
                recommendation_type=r["recommendation_type"],
                required_skills=career.get("required_skills", []),
                salary_range=career.get("salary_range"),
                min_education=career.get("min_education"),
                difficulty_level=career.get("difficulty_level", 3),
                work_style=career.get("work_style")
            ))
        
        # Determine method used
        method = "popularity" if not results else results[0].get("recommendation_type", "unknown")
        
        return RecommendationsResponse(
            user_email=user_email,
            recommendations=recommendations,
            total_count=len(recommendations),
            recommendation_method=method
        )
        
    except Exception as e:
        logger.error(f"Recommendation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting recommendations: {str(e)}")


@router.get("/similar/{career_name}", response_model=SimilarCareersResponse)
async def get_similar_careers(
    career_name: str,
    top_k: int = 3,
    db: AsyncSession = Depends(get_db)
):
    """
    Get careers similar to a given career.
    
    Useful for "You might also like" sections.
    """
    try:
        results = await RecommendationService.get_similar_careers(
            db=db,
            career_name=career_name,
            top_k=top_k
        )
        
        return SimilarCareersResponse(
            target_career=career_name,
            similar_careers=results
        )
        
    except Exception as e:
        logger.error(f"Similar careers error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# ================== INTERACTION TRACKING ==================

@router.post("/track", response_model=InteractionResponse)
async def track_interaction(
    request: InteractionTrackRequest,
    user_email: str,  # In production, get from auth token
    db: AsyncSession = Depends(get_db)
):
    """
    Track user interaction with a career.
    
    Used for collaborative filtering.
    
    Interaction types:
    - viewed: User viewed career details
    - saved: User bookmarked/saved the career
    - clicked_roadmap: User clicked to generate roadmap
    - dismissed: User explicitly dismissed recommendation
    """
    try:
        valid_types = ["viewed", "saved", "clicked_roadmap", "quiz_result", "dismissed"]
        if request.interaction_type not in valid_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid interaction type. Must be one of: {valid_types}"
            )
        
        interaction = await RecommendationService.track_interaction(
            db=db,
            user_email=user_email,
            career_name=request.career_name,
            interaction_type=request.interaction_type,
            source=request.source,
            session_id=request.session_id
        )
        
        return InteractionResponse(
            success=True,
            interaction_id=interaction.id,
            message=f"Tracked {request.interaction_type} for {request.career_name}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Interaction tracking error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# ================== FEEDBACK ==================

@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    request: RecommendationFeedbackRequest,
    user_email: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Submit feedback on a recommendation.
    
    Helps improve future recommendations.
    """
    try:
        # Track as positive or negative interaction
        interaction_type = "saved" if request.is_helpful else "dismissed"
        
        await RecommendationService.track_interaction(
            db=db,
            user_email=user_email,
            career_name=request.career_name,
            interaction_type=interaction_type,
            source="feedback"
        )
        
        return FeedbackResponse(
            success=True,
            message="Thank you for your feedback!"
        )
        
    except Exception as e:
        logger.error(f"Feedback error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
