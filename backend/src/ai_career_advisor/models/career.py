from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship

from ai_career_advisor.core.database import Base


class Career(Base):
    __tablename__ = "careers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, index=True)

    branch_id = Column(
        Integer,
        ForeignKey("branches.id", ondelete="CASCADE"),
        nullable=False
    )

    description = Column(Text, nullable=True)
    market_trend = Column(String(100), nullable=True)
    salary_range = Column(String(100), nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)

    # relationships
    branch = relationship("Branch", back_populates="careers")
    insight = relationship("CareerInsight", back_populates="career", uselist=False)

