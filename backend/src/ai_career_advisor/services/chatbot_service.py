import google.generativeai as genai
from ai_career_advisor.core.config import settings
from ai_career_advisor.core.logger import logger
from ai_career_advisor.services.intentfilter import IntentFilter
from ai_career_advisor.RAG.retriever import retriever
from ai_career_advisor.models.chatconversation import ChatConversation
from ai_career_advisor.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
import asyncio
from functools import partial
import time
import uuid

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")


class ChatbotService:
    
    @staticmethod
    async def ask(
        query: str,
        session_id: str = None,
        user_email: str = None,
        db: AsyncSession = None
    ) -> Dict[str, Any]:
        
        start_time = time.time()
        
        if not session_id:
            session_id = str(uuid.uuid4())
        
        logger.info(f"Chatbot query: {query} (session: {session_id})")
        
        intent_result = IntentFilter.is_career_related(query)
        
        if not intent_result["is_career"]:
            response_data = IntentFilter.get_rejection_message()
            
            if db:
                await ChatbotService._save_conversation(
                    db=db,
                    session_id=session_id,
                    user_email=user_email,
                    query=query,
                    response=response_data["response"],
                    response_type="rejected",
                    confidence=0.0,
                    response_time=time.time() - start_time,
                    sources=[]
                )
            
            return {
                "session_id": session_id,
                "query": query,
                "response": response_data["response"],
                "sources": [],
                "confidence": 0.0,
                "response_type": "rejected",
                "response_time": time.time() - start_time
            }
        
        rag_result = await retriever.search_and_build_context(query, top_k=5)
        
        if rag_result["found"] and rag_result["context"]:
            response_text = await ChatbotService._generate_with_rag(
                query=query,
                context=rag_result["context"]
            )
            response_type = "rag_verified"
            confidence = max(rag_result["scores"]) if rag_result["scores"] else 0.5
            sources = rag_result["sources"]

        else:
            response_text = await ChatbotService._generate_without_rag(query)
            response_type = "llm_generated"
            confidence = 0.6
            sources = []
            
            try:
                saved = await retriever.add_to_knowledge_base(
                    query=query,
                    response=response_text,
                    metadata={
                        "source": "llm_generated",
                        "session_id": session_id,
                        "timestamp": time.time()
                    }
                )
                
                if saved:
                    logger.success(f"LLM response saved to RAG for: {query[:50]}")
                    response_type = "llm_saved" 
                else:
                    logger.warning(" Failed to save to RAG")
            
            except Exception as e:
                logger.error(f" Error saving to RAG: {str(e)}")
        
        response_time = time.time() - start_time
        
        if db:
            await ChatbotService._save_conversation(
                db=db,
                session_id=session_id,
                user_email=user_email,
                query=query,
                response=response_text,
                response_type=response_type,
                confidence=confidence,
                response_time=response_time,
                sources=sources
            )
        
        return {
            "session_id": session_id,
            "query": query,
            "response": response_text,
            "sources": sources,
            "confidence": confidence,
            "response_type": response_type,
            "response_time": response_time
        }
    
    @staticmethod
    async def _generate_with_rag(query: str, context: str) -> str:
        prompt = f"""You are an AI Career Counselor for Indian students. Answer the user's question using ONLY the provided context.

CONTEXT (from verified database):
{context}

USER QUESTION: {query}

INSTRUCTIONS:
- Answer in the same language as the question (Hinglish/Hindi/English)
- Use ONLY information from the context above
- Be concise and helpful
- If context doesn't have exact answer, say "Based on available data..." and provide closest match
- Include specific details like fees, ranks, exam dates from context
- Keep response under 200 words

ANSWER:"""

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                partial(model.generate_content, prompt)
            )
            
            answer = response.text.strip()
            logger.success(f"RAG response generated ({len(answer)} chars)")
            return answer
        
        except Exception as e:
            logger.error(f"RAG generation error: {str(e)}")
            return "Sorry, I encountered an error. Please try again."
    
    @staticmethod
    async def _generate_without_rag(query: str) -> str:
        prompt = f"""You are an AI Career Counselor for Indian students. The user asked a career-related question but we don't have specific data in our database.

USER QUESTION: {query}

INSTRUCTIONS:
- Provide general helpful guidance about Indian education and careers
- Answer in the same language as the question (Hinglish/Hindi/English)
- Mention that this is general guidance and suggest checking official sources
- Keep response under 150 words
- Be honest if you're not certain

ANSWER:"""

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                partial(model.generate_content, prompt)
            )
            
            answer = response.text.strip()
            note = "\n\n⚠️ Note: Yeh general guidance hai. Official details ke liye college/exam website check karein."
            
            logger.info(f"LLM fallback response generated")
            return answer + note
        
        except Exception as e:
            logger.error(f"LLM generation error: {str(e)}")
            return "Sorry, I encountered an error. Please try again."
    
    @staticmethod
    async def _save_conversation(
        db: AsyncSession,
        session_id: str,
        user_email: str,
        query: str,
        response: str,
        response_type: str,
        confidence: float,
        response_time: float,
        sources: list
    ):
        try:
            conversation = ChatConversation(
                sessionid=session_id,
                useremail=user_email,
                userquery=query,
                botresponse=response,
                sources=sources,
                confidence=confidence,
                responsetype=response_type,
                responsetime=response_time
            )
            
            db.add(conversation)
            await db.commit()
            
            logger.debug(f"Conversation saved (session: {session_id})")
        
        except Exception as e:
            logger.error(f"Failed to save conversation: {str(e)}")
            await db.rollback()
