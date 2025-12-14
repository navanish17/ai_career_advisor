from sqlalchemy import Column, Integer, Float, String, Text, Boolean, DateTime, func
from ai_career_advisor.core.database import Base

class Degree(Base):
    __tablename__ = "degrees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), unique=True, nullable=False)
    stream = Column(String(50), index=True, nullable=False) 
    short_description = Column(Text, nullable=True) 
    duration_years = Column(Float, nullable=True)
    eligibility = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Degree id={self.id} name={self.name} stream={self.stream}>"
