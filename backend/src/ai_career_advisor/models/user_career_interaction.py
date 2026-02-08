"""
User Career Interactions Model
Tracks user interactions with careers for collaborative filtering
"""
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, Float, func
from ai_career_advisor.core.database import Base
from typing import Optional
import uuid


class UserCareerInteraction(Base):
    """
    Tracks user interactions with careers for collaborative filtering.
    
    Interaction types:
    - viewed: User viewed career details
    - saved: User bookmarked/saved the career
    - clicked_roadmap: User clicked to generate roadmap
    - dismissed: User explicitly dismissed recommendation
    
    Example:
        interaction = UserCareerInteraction(
            user_email="student@example.com",
            career_name="Software Engineer",
            interaction_type="clicked_roadmap",
            score=1.0
        )
    """
    __tablename__ = "user_career_interactions"
    
    id: Mapped[str] = mapped_column(
        String(36), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    
    # User identification
    user_email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    
    # Career identification
    career_name: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    
    # Interaction details
    interaction_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # Types: "viewed", "saved", "clicked_roadmap", "quiz_result", "dismissed"
    
    # Implicit rating score (for matrix factorization)
    # viewed = 0.3, saved = 0.7, clicked_roadmap = 1.0, dismissed = -0.5
    score: Mapped[float] = mapped_column(Float, default=0.5)
    
    # Source of interaction
    source: Mapped[Optional[str]] = mapped_column(String(50))  # "recommendation", "search", "chatbot"
    
    # Session tracking
    session_id: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Timestamp
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "user_email": self.user_email,
            "career_name": self.career_name,
            "interaction_type": self.interaction_type,
            "score": self.score,
            "source": self.source,
            "created_at": str(self.created_at) if self.created_at else None
        }


# Interaction score weights
INTERACTION_SCORES = {
    "viewed": 0.3,
    "saved": 0.7,
    "clicked_roadmap": 1.0,
    "quiz_result": 0.8,
    "dismissed": -0.5
}
