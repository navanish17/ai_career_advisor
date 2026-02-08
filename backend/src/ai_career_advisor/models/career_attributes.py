"""
Career Attributes Model
Stores career metadata for content-based recommendation matching
"""
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, Float, Text, func, JSON
from ai_career_advisor.core.database import Base
from typing import Optional, List
import uuid


class CareerAttributes(Base):
    """
    Stores career metadata used for matching with user preferences.
    
    Each career has:
    - Required skills (for skill matching)
    - Interest tags (for interest matching)
    - Education requirements
    - Salary and work style info
    
    Example:
        career = CareerAttributes(
            career_name="Software Engineer",
            required_skills=["python", "java", "problem_solving", "dsa"],
            interest_tags=["technology", "coding", "innovation"],
            min_education="graduate",
            salary_range="8-25LPA"
        )
    """
    __tablename__ = "career_attributes"
    
    id: Mapped[str] = mapped_column(
        String(36), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    
    # Career identification
    career_name: Mapped[str] = mapped_column(String(200), unique=True, index=True, nullable=False)
    career_category: Mapped[Optional[str]] = mapped_column(String(100))  # "technology", "healthcare", "finance"
    
    # Description
    short_description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Skills and interests (for content-based matching)
    required_skills: Mapped[list] = mapped_column(JSON, default=list)  # ["python", "sql", "communication"]
    interest_tags: Mapped[list] = mapped_column(JSON, default=list)  # ["technology", "data", "problem_solving"]
    personality_fit: Mapped[list] = mapped_column(JSON, default=list)  # ["analytical", "detail_oriented"]
    
    # Education requirements
    min_education: Mapped[Optional[str]] = mapped_column(String(50))  # "10th", "12th", "graduate", "postgraduate"
    preferred_streams: Mapped[list] = mapped_column(JSON, default=list)  # ["science", "commerce"]
    required_degrees: Mapped[list] = mapped_column(JSON, default=list)  # ["B.Tech", "BCA", "MCA"]
    
    # Career metrics
    salary_range: Mapped[Optional[str]] = mapped_column(String(50))  # "3-5LPA", "5-10LPA", etc.
    min_salary_lpa: Mapped[Optional[float]] = mapped_column(Float)  # For numeric comparison
    max_salary_lpa: Mapped[Optional[float]] = mapped_column(Float)
    
    # Work style
    work_style: Mapped[Optional[str]] = mapped_column(String(50))  # "remote", "office", "hybrid", "field"
    
    # Difficulty and growth
    difficulty_level: Mapped[int] = mapped_column(Integer, default=3)  # 1-5 scale
    growth_potential: Mapped[Optional[str]] = mapped_column(String(50))  # "high", "medium", "low"
    job_availability: Mapped[Optional[str]] = mapped_column(String(50))  # "high", "medium", "low"
    
    # Location relevance (for India-specific)
    top_cities: Mapped[list] = mapped_column(JSON, default=list)  # ["Bangalore", "Mumbai", "Delhi"]
    
    # Popularity score (for cold-start fallback)
    popularity_score: Mapped[float] = mapped_column(Float, default=0.5)  # 0-1 scale
    
    # Semantic Search (Phase 4)
    # Stores pre-calculated description embeddings for semantic matching
    semantic_vector: Mapped[Optional[list]] = mapped_column(JSON) 
    
    # Timestamps
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "career_name": self.career_name,
            "career_category": self.career_category,
            "short_description": self.short_description,
            "required_skills": self.required_skills or [],
            "interest_tags": self.interest_tags or [],
            "personality_fit": self.personality_fit or [],
            "min_education": self.min_education,
            "preferred_streams": self.preferred_streams or [],
            "required_degrees": self.required_degrees or [],
            "salary_range": self.salary_range,
            "work_style": self.work_style,
            "difficulty_level": self.difficulty_level,
            "growth_potential": self.growth_potential,
            "job_availability": self.job_availability,
            "top_cities": self.top_cities or [],
            "popularity_score": self.popularity_score
        }
    
    def get_attribute_vector(self) -> List[str]:
        """Get combined attributes for similarity matching"""
        return (
            (self.required_skills or []) + 
            (self.interest_tags or []) + 
            (self.personality_fit or [])
        )
