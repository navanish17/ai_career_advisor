from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean, DateTime
from sqlalchemy.sql import func
from ai_career_advisor.core.database import Base


class ExamAlert(Base):
    """
    Stores user alert preferences for entrance exams
    """
    __tablename__ = "exam_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User identification (email-based for now)
    user_email = Column(String(300), nullable=False, index=True)
    
    # Alert details
    entrance_exam_id = Column(Integer, ForeignKey("entrance_exams.id", ondelete="CASCADE"), nullable=False)
    alert_type = Column(String(50), nullable=False) 
    alert_date = Column(Date, nullable=False)  
    
    # Alert status
    is_sent = Column(Boolean, default=False, nullable=False, index=True)
    
    # Context (optional - for personalized email)
    college_name = Column(String(300), nullable=True)
    degree = Column(String(100), nullable=True)
    branch = Column(String(200), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_at = Column(DateTime(timezone=True), nullable=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_email": self.user_email,
            "entrance_exam_id": self.entrance_exam_id,
            "alert_type": self.alert_type,
            "alert_date": self.alert_date.isoformat() if self.alert_date else None,
            "is_sent": self.is_sent,
            "college_name": self.college_name,
            "degree": self.degree,
            "branch": self.branch,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
