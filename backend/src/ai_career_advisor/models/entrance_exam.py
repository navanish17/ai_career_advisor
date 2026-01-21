from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, Text
from sqlalchemy.sql import func
from ai_career_advisor.core.database import Base


class EntranceExam(Base):
    """
    Stores entrance exam information
    (JEE Main, NEET, CUET, CAT, etc.)
    """
    __tablename__ = "entrance_exams"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Exam identification
    exam_name = Column(String(100), nullable=False, unique=True, index=True)  
    exam_full_name = Column(String(300), nullable=True)  
    conducting_body = Column(String(200), nullable=True)  
    
    # Important dates
    exam_date = Column(Date, nullable=True)  
    registration_start_date = Column(Date, nullable=True)
    registration_end_date = Column(Date, nullable=True)
    
    # Exam details
    exam_pattern = Column(String(100), nullable=True)  
    official_website = Column(String(500), nullable=True)
    syllabus_link = Column(String(500), nullable=True)
    
    # Metadata
    academic_year = Column(String(20), nullable=True)  
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            "id": self.id,
            "exam_name": self.exam_name,
            "exam_full_name": self.exam_full_name,
            "conducting_body": self.conducting_body,
            "exam_date": self.exam_date.isoformat() if self.exam_date else None,
            "registration_start_date": self.registration_start_date.isoformat() if self.registration_start_date else None,
            "registration_end_date": self.registration_end_date.isoformat() if self.registration_end_date else None,
            "exam_pattern": self.exam_pattern,
            "official_website": self.official_website,
            "syllabus_link": self.syllabus_link,
            "academic_year": self.academic_year,
            "is_active": self.is_active
        }
