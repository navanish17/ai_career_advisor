from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from ai_career_advisor.core.database import Base


class CollegeProgramCache(Base):
    """Cache for college program availability checks"""
    __tablename__ = "college_program_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    college_id = Column(Integer, ForeignKey("colleges.id"), nullable=False)
    degree = Column(String(100), nullable=False)
    branch = Column(String(200), nullable=False)
    offers_program = Column(Boolean, nullable=False)
    checked_at = Column(DateTime(timezone=True), server_default=func.now())
