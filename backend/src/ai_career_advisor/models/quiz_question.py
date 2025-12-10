from sqlalchemy import String, Integer, DateTime, JSON, Column, func
from ai_career_advisor.core.database import Base

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key = True, index = True)
    question_text = Column(String, nullable = False)
    options = Column(JSON, nullable = False)
    score_mapping = Column(JSON, nullable = False)
    category = Column(String, nullable = True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
