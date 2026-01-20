from sqlalchemy import Column, Integer, String, JSON, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from ai_career_advisor.core.database import Base


class BackwardRoadmap(Base):
    """
    Stores user's backward career planning roadmaps
    Generated from career goal (e.g., "I want to become a Software Engineer")
    """
    __tablename__ = "backward_roadmaps"
    
    id = Column(Integer, primary_key=True, index=True)
    
   
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Input
    career_goal_input = Column(String(500), nullable=False)  
    

    normalized_career = Column(String(200), nullable=False, index=True)  
    career_category = Column(String(100), nullable=True) 
  
    career_description = Column(Text, nullable=True)  
    
    required_education = Column(JSON, nullable=True)  
    entrance_exams = Column(JSON, nullable=True)  
    stream_recommendation = Column(JSON, nullable=True)  
    
    skills_required = Column(JSON, nullable=True) 
    projects_to_build = Column(JSON, nullable=True)  
    internships = Column(JSON, nullable=True)  
    certifications = Column(JSON, nullable=True)  
    
    top_colleges = Column(JSON, nullable=True)  
    career_prospects = Column(JSON, nullable=True)  
    timeline = Column(JSON, nullable=True)  
    
    # Metadata
    source = Column(String(50), nullable=False, default="llm_generated")  
    confidence_score = Column(Float, nullable=True)  
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self):
        """Convert model to dictionary for API response"""
        return {
            "id": self.id,
            "career_goal_input": self.career_goal_input,
            "normalized_career": self.normalized_career,
            "career_category": self.career_category,
            "career_description": self.career_description,
            "required_education": self.required_education,
            "entrance_exams": self.entrance_exams,
            "stream_recommendation": self.stream_recommendation,
            "skills_required": self.skills_required,
            "projects_to_build": self.projects_to_build,
            "internships": self.internships,
            "certifications": self.certifications,
            "top_colleges": self.top_colleges,
            "career_prospects": self.career_prospects,
            "timeline": self.timeline,
            "source": self.source,
            "confidence_score": self.confidence_score,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
