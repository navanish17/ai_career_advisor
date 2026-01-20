from sqlalchemy import Column, Integer, String, JSON, Boolean, DateTime, Text
from sqlalchemy.sql import func
from ai_career_advisor.core.database import Base


class CareerTemplate(Base):
    """
    Pre-built roadmap templates for popular careers
    Used for fast response without LLM calls
    """
    __tablename__ = "career_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Career identification
    career_name = Column(String(200), unique=True, nullable=False, index=True)  # "Software Engineer"
    category = Column(String(100), nullable=True, index=True)  # "Technology"
    
    # Template data (same structure as BackwardRoadmap JSON fields)
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
    is_active = Column(Boolean, default=True, nullable=False)  # Can disable outdated templates
    version = Column(Integer, default=1)  # For template updates
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self):
        """Convert template to dictionary"""
        return {
            "career_name": self.career_name,
            "category": self.category,
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
            "source": "template",
            "version": self.version
        }
