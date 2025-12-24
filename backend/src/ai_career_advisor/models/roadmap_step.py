from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from ai_career_advisor.core.database import Base


class RoadmapStep(Base):
    __tablename__ = "roadmap_step"

    id = Column(Integer, primary_key=True, index=True)

    roadmap_id = Column(Integer, ForeignKey("roadmap.id"), nullable=False)

    step_order = Column(Integer, nullable=False)
    # 1,2,3,4,5,6

    step_type = Column(String, nullable=False)
    # class, stream, degree, branch, career, top_1_percent

    reference_table = Column(String, nullable=True)
    # stream, degree, branch, career, career_insight

    reference_id = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
