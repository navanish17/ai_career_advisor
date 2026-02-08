from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
from ai_career_advisor.core.database import Base

class Roadmap(Base):
    __tablename__ = "roadmap"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    class_level = Column(String, nullable=True)
    roadmap_type = Column(String, nullable=False)
    
    name = Column(String, nullable=True)
    share_token = Column(String, unique=True, index=True, nullable=True)
    career_goal = Column(String, nullable=True)
    roadmap_data = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
