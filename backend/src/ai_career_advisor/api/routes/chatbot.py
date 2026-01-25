from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ai_career_advisor.Schemas.chatbot import (
    IntentCheckRequest,
    IntentCheckResponse,
    ChatbotAskRequest,
    ChatbotAskResponse,
    ChatFeedbackRequest,
    ChatFeedbackResponse
)
from ai_career_advisor.services.intentfilter import IntentFilter
from ai_career_advisor.services.chatbot_service import ChatbotService
from ai_career_advisor.models.chatconversation import ChatConversation
from ai_career_advisor.core.database import get_db
from ai_career_advisor.core.logger import logger
from sqlalchemy import select

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])


@router.post("/check-intent", response_model=IntentCheckResponse)
async def check_intent(request: IntentCheckRequest):
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


@router.post("/ask", response_model=ChatbotAskResponse)
async def ask_chatbot(
    request: ChatbotAskRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        logger.info(f"Chatbot ask: {request.query}")
        
        result = await ChatbotService.ask(
            query=request.query,
            session_id=request.sessionid,
            user_email=None,
            db=db
        )
        
        return {
            "query": result["query"],
            "response": result["response"],
            "sources": result.get("sources", []),
            "confidence": result["confidence"],
            "responsetype": result["response_type"],
            "responsetime": result["response_time"],
            "sessionid": result["session_id"]
        }
    
    except Exception as e:
        logger.error(f"Chatbot ask error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/history/{sessionid}")
async def get_conversation_history(
    sessionid: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(
            select(ChatConversation)
            .where(ChatConversation.sessionid == sessionid)
            .order_by(ChatConversation.createdat.desc())
        )
        conversations = result.scalars().all()
        
        return {
            "sessionid": sessionid,
            "conversations": [conv.to_dict() for conv in conversations],
            "total": len(conversations)
        }
    
    except Exception as e:
        logger.error(f"History fetch error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/feedback", response_model=ChatFeedbackResponse)
async def submit_feedback(
    request: ChatFeedbackRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(
            select(ChatConversation)
            .where(ChatConversation.id == request.conversationid)
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        conversation.upvoted = request.upvoted
        conversation.feedbacktext = request.feedbacktext
        
        await db.commit()
        
        logger.info(f"Feedback saved for conversation {request.conversationid}")
        
        return {
            "success": True,
            "message": "Feedback saved successfully",
            "conversationid": request.conversationid
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Feedback error: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
