"""
Recommendation System Pydantic Schemas
Request/Response models for recommendation API endpoints
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# ================== QUIZ/PREFERENCES SCHEMAS ==================

class QuizSubmitRequest(BaseModel):
    """Request body for submitting career quiz answers"""
    skills: List[str] = Field(default_factory=list, description="User's skills")
    interests: List[str] = Field(default_factory=list, description="User's interests")
    education_level: Optional[str] = Field(None, description="Current education: 10th, 12th, graduate, postgraduate")
    current_stream: Optional[str] = Field(None, description="Stream: science, commerce, arts")
    percentage: Optional[float] = Field(None, ge=0, le=100, description="Academic percentage")
    preferred_work_style: Optional[str] = Field(None, description="Work preference: remote, office, hybrid")
    preferred_salary_range: Optional[str] = Field(None, description="Salary expectation: 3-5LPA, 5-10LPA, etc.")
    preferred_location: Optional[str] = Field(None, description="Preferred city")
    personality_traits: List[str] = Field(default_factory=list, description="Personality: analytical, creative, etc.")
    budget_constraint: Optional[str] = Field(None, description="Education budget limit")
    time_commitment: Optional[str] = Field(None, description="Availability: full_time, part_time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "skills": ["python", "communication", "problem_solving"],
                "interests": ["technology", "finance"],
                "education_level": "12th",
                "current_stream": "science",
                "percentage": 85.5,
                "preferred_work_style": "hybrid",
                "preferred_salary_range": "5-10LPA",
                "personality_traits": ["analytical", "detail_oriented"]
            }
        }


class UserPreferencesResponse(BaseModel):
    """Response for user preferences"""
    id: str
    user_email: str
    skills: List[str]
    interests: List[str]
    education_level: Optional[str]
    current_stream: Optional[str]
    preferred_work_style: Optional[str]
    preferred_salary_range: Optional[str]
    quiz_completed: bool
    quiz_completion_percentage: int


# ================== RECOMMENDATION SCHEMAS ==================

class CareerRecommendation(BaseModel):
    """Single career recommendation with match score"""
    career_name: str
    career_category: Optional[str]
    short_description: Optional[str]
    match_score: float = Field(..., description="Match percentage (0-100)")
    content_score: Optional[float] = Field(None, description="Content-based score")
    recommendation_type: str = Field(..., description="Type: content_based, hybrid, popularity")
    required_skills: List[str]
    salary_range: Optional[str]
    min_education: Optional[str]
    difficulty_level: int
    work_style: Optional[str]


class RecommendationsResponse(BaseModel):
    """Response for career recommendations"""
    user_email: str
    recommendations: List[CareerRecommendation]
    total_count: int
    recommendation_method: str


class SimilarCareersResponse(BaseModel):
    """Response for similar careers"""
    target_career: str
    similar_careers: List[dict]


# ================== INTERACTION SCHEMAS ==================

class InteractionTrackRequest(BaseModel):
    """Request to track user-career interaction"""
    career_name: str
    interaction_type: str = Field(..., description="Type: viewed, saved, clicked_roadmap, dismissed")
    source: Optional[str] = Field("recommendation", description="Where interaction occurred")
    session_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "career_name": "Software Engineer",
                "interaction_type": "clicked_roadmap",
                "source": "recommendation"
            }
        }


class InteractionResponse(BaseModel):
    """Response for interaction tracking"""
    success: bool
    interaction_id: str
    message: str


# ================== FEEDBACK SCHEMAS ==================

class RecommendationFeedbackRequest(BaseModel):
    """User feedback on recommendations"""
    career_name: str
    is_helpful: bool
    feedback_text: Optional[str] = None


class FeedbackResponse(BaseModel):
    """Response for feedback submission"""
    success: bool
    message: str
