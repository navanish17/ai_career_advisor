from sqlalchemy import Column, Integer, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship

from ai_career_advisor.core.database import Base


class CareerInsight(Base):
    __tablename__ = "career_insights"

    id = Column(Integer, primary_key=True, index=True)

    career_id = Column(
        Integer,
        ForeignKey("careers.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )

    skills = Column(JSON, nullable=False)
    internships = Column(JSON, nullable=False)
    projects = Column(JSON, nullable=False)
    programs = Column(JSON, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)

    # relationship
    career = relationship("Career", back_populates="insight")
