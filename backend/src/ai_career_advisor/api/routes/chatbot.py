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
from ai_career_advisor.models.user import User
from ai_career_advisor.core.database import get_db
from ai_career_advisor.core.security import get_current_user
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
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        logger.info(f"Chatbot ask from user {current_user.email}: {request.query}")
        
        result = await ChatbotService.ask(
            query=request.query,
            session_id=request.sessionid,
            user_email=current_user.email,
            db=db,
            model_preference=request.model
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
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Get last 10 conversations for this session AND user (most recent first, then reverse for display)
        result = await db.execute(
            select(ChatConversation)
            .where(
                ChatConversation.sessionid == sessionid,
                ChatConversation.useremail == current_user.email
            )
            .order_by(ChatConversation.createdat.desc())
            .limit(10)  # Only last 10 conversations
        )
        conversations = result.scalars().all()
        
        # Reverse to show in chronological order (oldest first)
        conversations = list(reversed(conversations))
        
        return {
            "sessionid": sessionid,
            "conversations": [conv.to_dict() for conv in conversations],
            "total": len(conversations),
            "limited_to": 10
        }
    
    except Exception as e:
        logger.error(f"History fetch error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/feedback", response_model=ChatFeedbackResponse)
async def submit_feedback(
    request: ChatFeedbackRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        result = await db.execute(
            select(ChatConversation)
            .where(
                ChatConversation.id == request.conversationid,
                ChatConversation.useremail == current_user.email
            )
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found or unauthorized")
        
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
