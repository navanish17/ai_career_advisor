from pydantic import BaseModel
from typing import List,Dict,Optional 

class QuizQuestionResponse(BaseModel):
    """format for sending a question to frontend"""
    id:int
    question_text:str
    options: List[str]

    class Config:
        from_attributes = True

class QuizSubmitRequest(BaseModel):
    """format in which user submit the quiz"""
    answers: List[Dict[str,int]]

class QuizResultResponse(BaseModel):
    """format in Response sent to frontend"""
    top_interests : List[str]
    scores: Dict[str,int]
    recommendation: Optional[str] = None
    
