from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from ai_career_advisor.core.database import Base


class Roadmap(Base):
    __tablename__ = "roadmap"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    class_level = Column(String, nullable=False)  
    # "10th" or "12th"

    roadmap_type = Column(String, nullable=False)  
    # "guided" or "backward"

    created_at = Column(DateTime(timezone=True), server_default=func.now())
