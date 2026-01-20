from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# =============================
# REQUEST SCHEMAS
# =============================

class BackwardPlannerRequest(BaseModel):
    """
    User input for generating backward roadmap
    """
    career_goal: str = Field(
        ..., 
        min_length=3,
        max_length=500,
        description="Career goal (e.g., 'I want to become a Software Engineer')",
        examples=["Software Engineer", "Doctor", "IAS Officer"]
    )


# =============================
# RESPONSE SCHEMAS
# =============================

class BackwardRoadmapResponse(BaseModel):
    """
    Complete backward roadmap response
    Flexible schema to handle various LLM output formats
    """
    id: Optional[int] = None
    career_goal_input: str
    normalized_career: str
    career_category: Optional[str] = None
    career_description: Optional[str] = None
    
    # Flexible JSON fields - accepts any structure
    required_education: Optional[Any] = None  # Can be dict or list
    entrance_exams: Optional[Any] = None  # Can be list of dicts or strings
    stream_recommendation: Optional[Any] = None  # Can be dict or string
    
    skills_required: Optional[Any] = None  # Can be list of dicts or strings
    projects_to_build: Optional[Any] = None  # Can be list of strings or dicts
    internships: Optional[Any] = None  # Can be list of dicts
    certifications: Optional[Any] = None  # Can be list of strings OR dicts ← FIXED
    
    top_colleges: Optional[Any] = None  # Can be list of dicts
    career_prospects: Optional[Any] = None  # Can be dict
    timeline: Optional[Any] = None  # Can be dict
    
    source: str  # "template" or "llm_generated" or "cache"
    confidence_score: Optional[float] = None
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class BackwardPlannerErrorResponse(BaseModel):
    """Error response for invalid career goals"""
    error: str
    message: str
    suggestion: Optional[str] = None


class BackwardPlannerSuccessResponse(BaseModel):
    """Success response with roadmap"""
    success: bool = True
    source: str  # "template", "llm_generated", or "cache"
    roadmap: BackwardRoadmapResponse
