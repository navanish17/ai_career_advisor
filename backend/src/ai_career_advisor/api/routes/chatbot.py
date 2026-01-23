from fastapi import APIRouter, HTTPException
from ai_career_advisor.Schemas.chatbot import (
    IntentCheckRequest,
    IntentCheckResponse
)
from ai_career_advisor.services.intentfilter import IntentFilter
from ai_career_advisor.core.logger import logger

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

@router.post("/check-intent", response_model=IntentCheckResponse)
async def check_intent(request: IntentCheckRequest):
    """
    TEST ENDPOINT: Check if user query is career-related
    
    **Hybrid Intent Filter:**
    - Layer 1: Keyword-based (fast, 0.01 sec)
    - Layer 2: LLM-based (accurate, 1-2 sec)
    
    **Example Queries:**
    - Career: "IIT Bombay fees kya hai"
    - Non-career: "biryani recipe batao"
    - Edge case: "What should I do after PCM"
    """
    try:
        logger.info(f"Checking intent for: {request.query}")
        
        result = IntentFilter.is_career_related(request.query)
        
        return {
            "query": request.query,
            "is_career": result["is_career"],
            "confidence": result["confidence"],
            "method": result["method"],
            "reason": result["reason"]
        }
    
    except Exception as e:
        logger.error(f"Intent check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
