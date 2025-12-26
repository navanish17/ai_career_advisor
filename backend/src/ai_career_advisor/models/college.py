from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from ai_career_advisor.core.database import Base


class College(Base):
    __tablename__ = "colleges"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)

    nirf_rank = Column(Integer, nullable=True)
    website = Column(String(255), nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
