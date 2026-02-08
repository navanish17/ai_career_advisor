"""
User Preferences Model
Stores user's skills, interests, and preferences for career recommendations
"""
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, func, JSON
from ai_career_advisor.core.database import Base
from typing import Optional, List
import uuid


class UserPreferences(Base):
    """
    Stores user preferences collected via quiz for career recommendations.
    
    Example:
        user_preferences = UserPreferences(
            user_email="student@example.com",
            skills=["python", "communication", "problem_solving"],
            interests=["technology", "finance", "teaching"],
            education_level="12th",
            preferred_work_style="hybrid"
        )
    """
    __tablename__ = "user_preferences"
    
    id: Mapped[str] = mapped_column(
        String(36), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    
    # Link to user (can be email for now, FK to users table later)
    user_email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    
    # Core preferences (stored as JSON arrays)
    skills: Mapped[list] = mapped_column(JSON, default=list)  # ["python", "excel", "communication"]
    interests: Mapped[list] = mapped_column(JSON, default=list)  # ["technology", "healthcare", "arts"]
    
    # Education & background
    education_level: Mapped[Optional[str]] = mapped_column(String(50))  # "10th", "12th", "graduate", "postgraduate"
    current_stream: Mapped[Optional[str]] = mapped_column(String(50))  # "science", "commerce", "arts"
    percentage: Mapped[Optional[float]] = mapped_column(nullable=True)  # Academic percentage
    
    # Work preferences
    preferred_work_style: Mapped[Optional[str]] = mapped_column(String(50))  # "remote", "office", "hybrid"
    preferred_salary_range: Mapped[Optional[str]] = mapped_column(String(50))  # "3-5LPA", "5-10LPA", "10-20LPA", "20+LPA"
    preferred_location: Mapped[Optional[str]] = mapped_column(String(100))  # City preference
    
    # Personality traits (for better matching)
    personality_traits: Mapped[list] = mapped_column(JSON, default=list)  # ["analytical", "creative", "leadership"]
    
    # Constraints
    budget_constraint: Mapped[Optional[str]] = mapped_column(String(50))  # Education budget
    time_commitment: Mapped[Optional[str]] = mapped_column(String(50))  # "full_time", "part_time"
    
    # Quiz completion tracking
    quiz_completed: Mapped[bool] = mapped_column(default=False)
    quiz_completion_percentage: Mapped[int] = mapped_column(default=0)
    
    # Timestamps
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "user_email": self.user_email,
            "skills": self.skills or [],
            "interests": self.interests or [],
            "education_level": self.education_level,
            "current_stream": self.current_stream,
            "percentage": self.percentage,
            "preferred_work_style": self.preferred_work_style,
            "preferred_salary_range": self.preferred_salary_range,
            "preferred_location": self.preferred_location,
            "personality_traits": self.personality_traits or [],
            "budget_constraint": self.budget_constraint,
            "time_commitment": self.time_commitment,
            "quiz_completed": self.quiz_completed,
            "quiz_completion_percentage": self.quiz_completion_percentage
        }
    
    def get_profile_vector(self) -> List[str]:
        """Get combined profile for similarity matching"""
        return (self.skills or []) + (self.interests or []) + (self.personality_traits or [])
