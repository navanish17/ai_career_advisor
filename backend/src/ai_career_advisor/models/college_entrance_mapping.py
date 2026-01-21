from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from ai_career_advisor.core.database import Base


class CollegeEntranceMapping(Base):
    """
    Maps colleges to their required entrance exams
    Example: IIT Bombay, BTech CS → JEE Advanced
    """
    __tablename__ = "college_entrance_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # College details
    college_name = Column(String(300), nullable=False, index=True)  
    degree = Column(String(100), nullable=False, index=True) 
    branch = Column(String(200), nullable=True, index=True)  
    
    # Entrance exam reference
    entrance_exam_id = Column(Integer, ForeignKey("entrance_exams.id", ondelete="CASCADE"), nullable=False)
    
    # Additional info
    cutoff_rank = Column(String(100), nullable=True)  
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "college_name": self.college_name,
            "degree": self.degree,
            "branch": self.branch,
            "entrance_exam_id": self.entrance_exam_id,
            "cutoff_rank": self.cutoff_rank
        }
