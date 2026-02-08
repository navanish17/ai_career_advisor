"""
Intent Classification API Endpoint

This endpoint allows you to test the intent classifier directly.
Useful for debugging and demo during interviews.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from ai_career_advisor.services.intentfilter import IntentFilterML
from ai_career_advisor.core.logger import logger


router = APIRouter(prefix="/intent", tags=["Intent Classification"])


class IntentRequest(BaseModel):
    """Request model for intent classification"""
    query: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "How to become a data scientist?"
            }
        }


class BatchIntentRequest(BaseModel):
    """Request model for batch intent classification"""
    queries: List[str]


class IntentResponse(BaseModel):
    """Response model for intent classification"""
    query: str
    is_career: bool
    intent: Optional[str]
    confidence: float
    method: str
    reason: str
    is_greeting: Optional[bool] = False
    is_farewell: Optional[bool] = False


class DetailedIntentResponse(BaseModel):
    """Detailed response with all probabilities"""
    text: str
    predicted_intent: str
    confidence: float
    all_probabilities: Dict[str, float]
    model_available: Optional[bool] = True


@router.post("/classify", response_model=IntentResponse)
async def classify_intent(request: IntentRequest):
    """
    Classify the intent of a user query
    
    📚 INTERVIEW USE:
    Test this endpoint to show how your ML model works.
    
    Example:
    curl -X POST "http://localhost:8000/api/intent/classify" \
         -H "Content-Type: application/json" \
         -d '{"query": "best colleges for computer science"}'
    """
    try:
        result = IntentFilterML.is_career_related(request.query)
        
        return IntentResponse(
            query=request.query,
            is_career=result.get("is_career", False),
            intent=result.get("intent"),
            confidence=result.get("confidence", 0),
            method=result.get("method", "unknown"),
            reason=result.get("reason", ""),
            is_greeting=result.get("is_greeting", False),
            is_farewell=result.get("is_farewell", False)
        )
    except Exception as e:
        logger.error(f"Intent classification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/classify/detailed", response_model=DetailedIntentResponse)
async def classify_intent_detailed(request: IntentRequest):
    """
    Get detailed intent classification with all class probabilities
    
    📚 INTERVIEW USE:
    Show this to explain how the model gives probabilities for ALL intents.
    This demonstrates you understand multi-class classification.
    """
    try:
        result = IntentFilterML.get_intent_details(request.query)
        
        return DetailedIntentResponse(
            text=result.get("text", request.query),
            predicted_intent=result.get("predicted_intent", "unknown"),
            confidence=result.get("confidence", 0),
            all_probabilities=result.get("all_probabilities", {}),
            model_available=result.get("model_available", True)
        )
    except Exception as e:
        logger.error(f"Detailed intent classification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/classify/batch")
async def classify_batch(request: BatchIntentRequest):
    """
    Classify multiple queries at once
    
    Useful for evaluating model performance on a test set.
    """
    try:
        results = []
        for query in request.queries:
            result = IntentFilterML.is_career_related(query)
            results.append({
                "query": query,
                "intent": result.get("intent"),
                "confidence": result.get("confidence"),
                "method": result.get("method")
            })
        
        return {"results": results, "count": len(results)}
    
    except Exception as e:
        logger.error(f"Batch classification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/labels")
async def get_intent_labels():
    """
    Get list of all intent labels the model can predict
    
    📚 INTERVIEW USE:
    Shows the different categories your model handles.
    """
    return {
        "labels": [
            {"id": 0, "name": "greeting", "description": "User greetings like hello, hi"},
            {"id": 1, "name": "farewell", "description": "User farewells like bye, thanks"},
            {"id": 2, "name": "career_query", "description": "Questions about careers"},
            {"id": 3, "name": "college_query", "description": "Questions about colleges"},
            {"id": 4, "name": "roadmap_request", "description": "Requests for career roadmaps"},
            {"id": 5, "name": "exam_query", "description": "Questions about exams"},
            {"id": 6, "name": "degree_query", "description": "Questions about degrees"},
            {"id": 7, "name": "recommendation_request", "description": "Requests for career suggestions"},
            {"id": 8, "name": "off_topic", "description": "Non-career related queries"}
        ],
        "total_labels": 9
    }


@router.get("/health")
async def intent_classifier_health():
    """
    Check if the ML intent classifier is loaded and working
    """
    try:
        # Test with a sample query
        result = IntentFilterML.is_career_related("test query")
        
        return {
            "status": "healthy",
            "ml_model_active": result.get("method") == "ml",
            "fallback_active": result.get("method") in ["keyword", "default"],
            "test_query": "test query",
            "test_result": result
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
