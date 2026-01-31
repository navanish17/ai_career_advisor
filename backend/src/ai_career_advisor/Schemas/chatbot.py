from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class IntentCheckRequest(BaseModel):
    query: str = Field(
        ..., 
        min_length=1, 
        max_length=500, 
        description="User query to check",
        example="IIT Bombay CSE fees kya hai"
    )


class IntentCheckResponse(BaseModel):
    query: str
    is_career: bool
    confidence: float
    method: str
    reason: str


class ChatbotAskRequest(BaseModel):
    query: str = Field(
        ..., 
        min_length=1,  # Allow short greetings like "hi"
        max_length=500, 
        description="User's career-related question",
        example="Software engineer kaise bane?"
    )
    sessionid: Optional[str] = Field(
        None, 
        description="Session ID for conversation tracking"
    )


class ChatbotAskResponse(BaseModel):
    query: str
    response: str
    sources: List[str] = []
    confidence: float
    responsetype: str
    responsetime: Optional[float] = None
    sessionid: str


class ChatHistoryResponse(BaseModel):
    id: int
    sessionid: str
    userquery: str
    botresponse: str
    sources: Optional[List[str]] = []
    confidence: Optional[float] = None
    responsetype: str
    responsetime: Optional[float] = None
    createdat: str


class ChatHistoryListResponse(BaseModel):
    sessionid: str
    conversations: List[ChatHistoryResponse]
    total: int


class ChatFeedbackRequest(BaseModel):
    conversationid: int = Field(..., description="ID of the conversation")
    upvoted: bool = Field(..., description="True for thumbs up, False for thumbs down")
    feedbacktext: Optional[str] = Field(
        None, 
        max_length=500, 
        description="Optional feedback text"
    )


class ChatFeedbackResponse(BaseModel):
    success: bool
    message: str
    conversationid: int
