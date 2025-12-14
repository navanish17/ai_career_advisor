from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from ai_career_advisor.core.database import Base


class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(120), nullable=False, index=True)

    degree_id = Column(
        Integer,
        ForeignKey("degrees.id", ondelete="CASCADE"),
        nullable=False
    )

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # relationship
    degree = relationship("Degree", backref="branches")
