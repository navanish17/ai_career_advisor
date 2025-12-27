from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func

from ai_career_advisor.core.database import Base


class CollegeDetails(Base):
    __tablename__ = "college_details"

    id = Column(Integer, primary_key=True, index=True)

    college_id = Column(
        Integer,
        ForeignKey("colleges.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    degrees = Column(JSON, nullable=True)          # ["BTech", "MTech"]
    entrance_exam = Column(String(100), nullable=True)
    fees = Column(String(100), nullable=True)
    avg_package = Column(String(100), nullable=True)

    source_urls = Column(JSON, nullable=True)

    last_fetched_at = Column(DateTime, server_default=func.now())
