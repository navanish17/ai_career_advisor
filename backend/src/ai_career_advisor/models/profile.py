from sqlalchemy import Column, String, Integer, ForeignKey, JSON, DateTime, func
from sqlalchemy.orm import relationship
from ai_career_advisor.core.database import Base

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)

    class_level = Column(String, nullable=True)
    location = Column(String, nullable=True)
    language = Column(String, nullable=True)

    known_interests = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user = relationship("User", back_populates="profile")
   



