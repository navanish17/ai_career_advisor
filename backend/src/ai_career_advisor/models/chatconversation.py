from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from ai_career_advisor.core.database import Base

class ChatConversation(Base):
    """
    Stores all chatbot conversations for analytics and learning
    """
    __tablename__ = "chatconversations"
    

    id = Column(Integer, primary_key=True, index=True)
    
    
    sessionid = Column(String(100), index=True, nullable=False)
    
    
    useremail = Column(String(255), nullable=True, index=True)
    
  
    userquery = Column(Text, nullable=False)
    botresponse = Column(Text, nullable=False)
    
 
    sources = Column(JSON, nullable=True)  
    ragscore = Column(Float, nullable=True)  
    confidence = Column(Float, nullable=True)  
    
 
    responsetype = Column(String(50), nullable=False)  
    
    
   
    responsetime = Column(Float, nullable=True)  # In seconds
    
    upvoted = Column(Boolean, default=None, nullable=True)
    feedbacktext = Column(Text, nullable=True)
    
  
    createdat = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "sessionid": self.sessionid,
            "userquery": self.userquery,
            "botresponse": self.botresponse,
            "sources": self.sources,
            "confidence": self.confidence,
            "responsetype": self.responsetype,
            "responsetime": self.responsetime,
            "createdat": self.createdat.isoformat() if self.createdat else None
        }
