"""
Agent Tools for Career Counselor
Wraps existing services as LangGraph-compatible tools
"""
from typing import Dict, Any, List
from langchain_core.tools import tool
from sqlalchemy.ext.asyncio import AsyncSession
from ai_career_advisor.core.logger import logger


@tool
async def recommend_careers_tool(
    user_email: str,
    db: AsyncSession,
    top_k: int = 5
) -> Dict[str, Any]:
    """
    Recommend careers based on user preferences using semantic search.
    
    Args:
        user_email: User's email address
        db: Database session
        top_k: Number of recommendations to return
        
    Returns:
        Dictionary with career recommendations and match scores
    """
    try:
        from ai_career_advisor.services.recommendation_service import RecommendationService
        
        recommendations = await RecommendationService.get_recommendations(
            db=db,
            user_email=user_email,
            top_k=top_k
        )
        
        return {
            "success": True,
            "recommendations": recommendations,
            "count": len(recommendations)
        }
    except Exception as e:
        logger.error(f"Recommendation tool error: {e}")
        return {
            "success": False,
            "error": str(e),
            "recommendations": []
        }


@tool
async def get_roadmap_tool(
    career_name: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Get career roadmap from database.
    
    Args:
        career_name: Name of the career
        db: Database session
        
    Returns:
        Dictionary with roadmap details or error
    """
    try:
        from ai_career_advisor.services.backward_roadmap_service import BackwardRoadmapService
        
        roadmap = await BackwardRoadmapService.get_by_career(
            db=db,
            career_name=career_name
        )
        
        if not roadmap:
            return {
                "success": False,
                "message": f"No roadmap found for {career_name}",
                "roadmap": None
            }
        
        return {
            "success": True,
            "roadmap": {
                "career": roadmap.normalized_career,
                "description": roadmap.career_description,
                "exams": roadmap.entrance_exams[:5] if roadmap.entrance_exams else [],
                "colleges": roadmap.top_colleges[:5] if roadmap.top_colleges else [],
                "salary": roadmap.career_prospects.get("salary_range") if roadmap.career_prospects else None
            }
        }
    except Exception as e:
        logger.error(f"Roadmap tool error: {e}")
        return {
            "success": False,
            "error": str(e),
            "roadmap": None
        }


@tool
async def search_web_tool(query: str) -> Dict[str, Any]:
    """
    Search the web using Perplexity API for current information.
    
    Args:
        query: Search query
        
    Returns:
        Dictionary with search results and sources
    """
    try:
        from ai_career_advisor.core.config import settings
        import httpx
        
        PERPLEXITY_API_KEY = settings.PERPLEXITY_API_KEY
        
        if not PERPLEXITY_API_KEY:
            return {
                "success": False,
                "error": "Perplexity API key not configured"
            }
        
        prompt = f"""You are an AI Career Counselor for Indian students.

QUESTION: {query}

INSTRUCTIONS:
- Search for current, accurate information about Indian education and careers
- Provide specific details: fees, eligibility, dates, salary ranges
- Keep response under 250 words
- Be factual and cite official sources"""

        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "sonar",
                    "messages": [
                        {"role": "system", "content": "You are an expert Indian education and career counselor."},
                        {"role": "user", "content": prompt}
                    ]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data["choices"][0]["message"]["content"].strip()
                citations = data.get("citations", [])
                
                return {
                    "success": True,
                    "answer": answer,
                    "sources": citations[:5] if citations else ["Web Search"]
                }
            else:
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}"
                }
                
    except Exception as e:
        logger.error(f"Web search tool error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@tool
async def search_rag_tool(query: str) -> Dict[str, Any]:
    """
    Search the RAG knowledge base for verified information.
    
    Args:
        query: Search query
        
    Returns:
        Dictionary with context and sources
    """
    try:
        from ai_career_advisor.RAG.retriever import retriever
        
        result = await retriever.search_and_build_context(query, top_k=5)
        
        if result["found"]:
            return {
                "success": True,
                "context": result["context"],
                "sources": result.get("sources", []),
                "num_documents": result.get("num_documents", 0)
            }
        else:
            return {
                "success": False,
                "message": "No relevant documents found in knowledge base"
            }
            
    except Exception as e:
        logger.error(f"RAG search tool error: {e}")
        return {
            "success": False,
            "error": str(e)
        }
