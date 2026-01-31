from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from ai_career_advisor.core.database import Base


class CareerInsight(Base):
    __tablename__ = "career_insights"

    id = Column(Integer, primary_key=True, index=True)
    career_id = Column(Integer, ForeignKey("careers.id"), unique=True, nullable=False)
    
    skills = Column(JSON, nullable=False)
    internships = Column(JSON, nullable=False)
    projects = Column(JSON, nullable=False)
    programs = Column(JSON, nullable=False)
    top_salary = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Relationship
    career = relationship("Career", back_populates="insight")
