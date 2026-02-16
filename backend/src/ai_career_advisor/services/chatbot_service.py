from ai_career_advisor.core.config import settings
from ai_career_advisor.core.logger import logger
from ai_career_advisor.services.intentfilter import IntentFilter
from ai_career_advisor.models.chatconversation import ChatConversation
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Tuple
import httpx
import time
import uuid
import re
import os

# Phase 4: LangGraph Agent (feature flag)
USE_AGENT_GRAPH = os.getenv("USE_AGENT_GRAPH", "true").lower() == "true"


class ChatbotService:
    """
    Robust AI Career Chatbot Service
    Features:
    - English by default, Hindi only when user asks in Hindi
    - RAG-first with Perplexity fallback
    - Sources ALWAYS provided
    - Feature detection with clickable links
    - Never crashes - all errors handled gracefully
    """
    
    # Feature patterns for recommending app features
    FEATURE_PATTERNS = {
        "stream": {
            "keywords": ["stream", "which stream", "science or commerce", "arts or science", "10th ke baad", "after 10th", "stream select", "konsa stream"],
            "link": "/stream-finder",
            "message": "\n\n🎯 **Want personalized stream recommendation?**\n👉 [Click here to use our Stream Finder](/stream-finder)"
        },
        "roadmap": {
            "keywords": [
                "roadmap", "how to become", "become a ", "become an ", "want to become",
                "kaise bane", "kaise banu", "banna hai", "banna chahta",
                "career path", "step by step", "guide to become", "steps to become",
                "what after 12th", "12th ke baad", "after 12th", "after graduation",
                "software engineer", "data scientist", "doctor", "lawyer", "ca ", "chartered accountant",
                "engineer", "developer", "designer", "manager"
            ],
            "link": "/roadmap/backward",
            "message": "\n\n🗺️ **Get a detailed career roadmap!**\n👉 [Generate your personalized roadmap here](/roadmap/backward)"
        },
        "college": {
            "keywords": ["college find", "find college", "best college", "top college", "college for", "iit admission", "nit admission", "bits", "college recommendation", "suggest college", "college finder", "search college"],
            "link": "/college-finder",
            "message": "\n\n🏫 **Looking for the perfect college?**\n👉 [Use our College Finder tool](/college-finder)"
        }
    }
    
    # Hindi detection patterns
    HINDI_PATTERNS = [
        r'[\u0900-\u097F]',  # Devanagari script
        r'\b(kya|kaise|kab|kaun|kahaan|kyun|kaha|hai|hoon|tum|aap|mujhe|mera|tera|uska|unka|hum|kon|kuch|bahut|accha|acha|bhi|nahi|nahin|se|ka|ki|ke|ko|me|ye|wo|woh|tha|thi|the|ho|raha|rahi|rahe|kar|karo|karna|karenge|karoge|bata|batao|batana)\b',  # Common Hindi words in Roman
    ]
    
    @staticmethod
    def _is_hindi_query(query: str) -> bool:
        """Detect if user query is in Hindi/Hinglish"""
        # Check for Devanagari script
        if re.search(r'[\u0900-\u097F]', query):
            return True
        
        # Check for common Hindi words (Hinglish)
        hindi_words = ['kya', 'kaise', 'hai', 'hoon', 'mujhe', 'batao', 'bata', 'karo', 
                       'chahiye', 'karenge', 'hoga', 'hogi', 'karna', 'padhna', 'padhai',
                       'kaun', 'konsa', 'kaunsa', 'baad', 'pehle', 'accha', 'theek', 'sahi']
        query_lower = query.lower()
        hindi_count = sum(1 for word in hindi_words if word in query_lower)
        
        # If 2+ Hindi words found, treat as Hindi
        return hindi_count >= 2
    
    @staticmethod
    async def ask(
        query: str,
        session_id: str = None,
        user_email: str = None,
        db: AsyncSession = None,
        model_preference: str = "auto"
    ) -> Dict[str, Any]:
        """
        Main chatbot entry point
        Returns response for any query - never fails
        ALWAYS includes sources in the response
        """
        start_time = time.time()
        
        if not session_id:
            session_id = str(uuid.uuid4())
        
        logger.info(f"💬 Chatbot query: {query} (session: {session_id})")
        
        # Detect language preference
        use_hindi = ChatbotService._is_hindi_query(query)
        logger.info(f"🌐 Language: {'Hindi/Hinglish' if use_hindi else 'English'}")
        
        # Phase 4: Use LangGraph Agent if enabled
        if USE_AGENT_GRAPH:
            try:
                from ai_career_advisor.agents.career_agent import CareerAgent
                
                agent = CareerAgent(db=db)
                result = await agent.run(
                    query=query,
                    user_email=user_email or "anonymous",
                    session_id=session_id,
                    language="hi" if use_hindi else "en",
                    model_preference=model_preference
                )
                
                if result["success"]:
                    response_text = result["response"]
                    
                    # Add feature links
                    feature_links = ChatbotService._detect_features(query)
                    if feature_links:
                        response_text += feature_links
                    
                    # Add sources
                    tool_outputs = result.get("tool_outputs", {})
                    sources = tool_outputs.get("extra_sources", ["AI Agent - Career Pilot"])
                    
                    # If agent already formatted sources in text, we don't need to append them again
                    # But if sources is just a list, we format it here
                    # Check if response already contains "References:"
                    if "**References:**" not in response_text:
                        sources_text = ChatbotService._format_sources(sources, "agent")
                        if sources_text:
                            response_text += sources_text
                    
                    response_time = time.time() - start_time
                    
                    await ChatbotService._save_conversation(
                        db, session_id, user_email, query, response_text,
                        "agent", 0.9, response_time, sources
                    )
                    
                    return {
                        "session_id": session_id,
                        "query": query,
                        "response": response_text,
                        "sources": sources,
                        "confidence": 0.9,
                        "response_type": "agent",
                        "response_time": response_time
                    }
            except Exception as e:
                logger.warning(f"Agent failed, falling back to legacy: {e}")
                # Fall through to legacy implementation
        
        try:
            # Step 1: Check intent (greetings, career, or blocked)
            intent_result = IntentFilter.is_career_related(query)
            
            # Handle greetings instantly (no API calls)
            if intent_result.get("is_greeting"):
                return await ChatbotService._handle_greeting(
                    query, session_id, user_email, db, start_time, use_hindi
                )
            
            # Handle blocked queries
            if not intent_result["is_career"]:
                return await ChatbotService._handle_rejection(
                    query, session_id, user_email, db, start_time, use_hindi
                )
            
            # Step 2: FEATURE ROUTING - Check if intent matches a feature
            # For roadmap requests, query existing roadmaps from BackwardPlanner feature
            detected_intent = intent_result.get("intent", "")
            
            # KEYWORD OVERRIDE: Force roadmap routing for "I want to become X" queries
            # (ML model sometimes classifies these as career_query instead of roadmap_request)
            query_lower = query.lower()
            roadmap_keywords = [
                "want to become", "wanna become", "become a ", "become an ",
                "how to become", "kaise bane", "kaise banu", "banna hai",
                "banna chahta", "banna chahti", "roadmap for", "path to become",
                "steps to become", "guide to become"
            ]
            if any(kw in query_lower for kw in roadmap_keywords):
                detected_intent = "roadmap_request"
                logger.info(f"🔀 Keyword override: treating as roadmap_request")
            
            if detected_intent == "roadmap_request":
                feature_response = await ChatbotService._handle_roadmap_request(
                    query, session_id, user_email, db, start_time, use_hindi
                )
                if feature_response:
                    return feature_response
            
            # Step 3: Try RAG for other queries (with error handling)
            rag_result = await ChatbotService._safe_rag_search(query)
            
            # Step 3: Generate response with sources
            if rag_result["found"] and rag_result.get("context"):
                # RAG has data - use it
                response_text, sources = await ChatbotService._generate_with_rag(
                    query, rag_result["context"], rag_result.get("sources", []), use_hindi
                )
                response_type = "rag_verified"
                confidence = max(rag_result.get("scores", [0.5]))
            else:
                # Use Perplexity Sonar with web search - ALWAYS get sources
                response_text, sources = await ChatbotService._generate_with_perplexity(query, use_hindi)
                response_type = "perplexity_search"
                confidence = 0.8
                
                # Try to save to RAG for future (non-blocking)
                await ChatbotService._save_to_rag(query, response_text, session_id)
            
            # Step 4: Detect features and add redirect links
            feature_links = ChatbotService._detect_features(query)
            if feature_links:
                response_text += feature_links
            
            # Step 5: Format sources into response with data source indicator
            sources_text = ChatbotService._format_sources(sources, response_type)
            if sources_text:
                response_text += sources_text
            
            response_time = time.time() - start_time
            
            # Save conversation
            await ChatbotService._save_conversation(
                db, session_id, user_email, query, response_text,
                response_type, confidence, response_time, sources
            )
            
            logger.success(f"✅ Response generated in {response_time:.2f}s ({response_type})")
            
            return {
                "session_id": session_id,
                "query": query,
                "response": response_text,
                "sources": sources,
                "confidence": confidence,
                "response_type": response_type,
                "response_time": response_time
            }
        
        except Exception as e:
            # Ultimate fallback - should never reach here
            logger.error(f"❌ Critical error: {str(e)}")
            return {
                "session_id": session_id,
                "query": query,
                "response": "I apologize, but I'm having technical difficulties. Please try again in a moment.",
                "sources": ["System Error"],
                "confidence": 0.0,
                "response_type": "error",
                "response_time": time.time() - start_time
            }
    
    @staticmethod
    def _format_sources(sources: List[str], response_type: str = "") -> str:
        """Format sources into a readable string with clickable links"""
        if not sources:
            return ""
        
        # Clean and deduplicate sources
        clean_sources = list(set([s for s in sources if s and s not in ["web_search", "System Error"]]))
        
        if not clean_sources:
            return ""
        
        # Add data source indicator with different symbols
        source_indicators = {
            "feature_db": "🗄️ *Source: Database*",
            "rag_verified": "📚 *Source: Knowledge Base*",
            "perplexity_search": "🌐 *Source: Web*",
            "greeting": "🤖 *Source: System*",
        }
        
        indicator = source_indicators.get(response_type, "")
        source_text = f"\n\n{indicator}\n\n**References:**\n" if indicator else "\n\n**References:**\n"
        
        for i, source in enumerate(clean_sources[:5], 1):  # Max 5 sources
            # Make URLs clickable in markdown with clean domain text
            if source.startswith("http://") or source.startswith("https://"):
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(source)
                    domain = parsed.netloc.replace("www.", "")
                    # Keep path if short, otherwise just domain
                    link_text = domain
                    source_text += f"{i}. [{link_text}]({source})\n"
                except:
                    source_text += f"{i}. [{source}]({source})\n"
            else:
                source_text += f"{i}. {source}\n"
        
        return source_text
    
    @staticmethod
    async def _handle_greeting(query: str, session_id: str, user_email: str, 
                                db: AsyncSession, start_time: float, use_hindi: bool) -> Dict[str, Any]:
        """Handle greetings instantly without any API calls"""
        if use_hindi:
            greeting_response = """👋 **Namaste! Main aapka AI Career Counselor hoon!**

Main Indian students ko education aur career guidance deta hoon. 🎓

**Aap mujhse puch sakte ho:**
- 💼 Career options (Engineering, Medical, Commerce, Arts)
- 🏫 College selection (IITs, NITs, Private colleges)
- 📝 Entrance exams (JEE, NEET, CUET, CAT, GATE)
- 💰 Fees, placements, salaries
- 📚 Study tips aur career roadmaps

Apna question poocho! 😊"""
        else:
            greeting_response = """👋 **Hello! I'm your AI Career Counselor!**

I help Indian students with education and career guidance. 🎓

**You can ask me about:**
- 💼 Career options (Engineering, Medical, Commerce, Arts)
- 🏫 College selection (IITs, NITs, Private colleges)
- 📝 Entrance exams (JEE, NEET, CUET, CAT, GATE)
- 💰 Fees, placements, and salaries
- 📚 Study tips and career roadmaps

Ask me your question! 😊"""
        
        response_time = time.time() - start_time
        
        await ChatbotService._save_conversation(
            db, session_id, user_email, query, greeting_response,
            "greeting", 1.0, response_time, ["AI Career Counselor"]
        )
        
        return {
            "session_id": session_id,
            "query": query,
            "response": greeting_response,
            "sources": ["AI Career Counselor"],
            "confidence": 1.0,
            "response_type": "greeting",
            "response_time": response_time
        }
    
    @staticmethod
    async def _handle_rejection(query: str, session_id: str, user_email: str,
                                 db: AsyncSession, start_time: float, use_hindi: bool) -> Dict[str, Any]:
        """Handle non-career queries with helpful redirection"""
        if use_hindi:
            rejection_response = """🎓 Main ek **AI Career Counselor** hoon for Indian students!

Main sirf **education aur career** related questions answer karta hoon:
- ✅ Career guidance (after 10th/12th)
- ✅ College selection (IITs, NITs, top colleges)
- ✅ Entrance exams (JEE, NEET, CUET)
- ✅ Career roadmaps (Software Engineer, Doctor, CA)
- ✅ Salary & job prospects

Koi career ya education-related question poocho! 😊"""
        else:
            rejection_response = """🎓 I'm an **AI Career Counselor** for Indian students!

I only answer **education and career** related questions:
- ✅ Career guidance (after 10th/12th)
- ✅ College selection (IITs, NITs, top colleges)
- ✅ Entrance exams (JEE, NEET, CUET)
- ✅ Career roadmaps (Software Engineer, Doctor, CA)
- ✅ Salary & job prospects

Please ask a career or education-related question! 😊"""
        
        response_time = time.time() - start_time
        
        await ChatbotService._save_conversation(
            db, session_id, user_email, query, rejection_response,
            "rejected", 0.0, response_time, ["AI Career Counselor - Topic Filter"]
        )
        
        return {
            "session_id": session_id,
            "query": query,
            "response": rejection_response,
            "sources": ["AI Career Counselor - Topic Filter"],
            "confidence": 0.0,
            "response_type": "rejected",
            "response_time": response_time
        }
    
    @staticmethod
    async def _handle_roadmap_request(
        query: str, session_id: str, user_email: str,
        db: AsyncSession, start_time: float, use_hindi: bool
    ) -> Dict[str, Any]:
        """
        Handle roadmap requests by checking existing BackwardPlanner data first.
        Returns short summary + redirect link to full feature.
        Returns None if no existing roadmap found (falls back to RAG/LLM).
        """
        try:
            # Extract career name from query
            career_name = ChatbotService._extract_career_from_query(query)
            
            if not career_name or not db:
                return None
            
            # Query existing roadmap from BackwardPlanner feature database
            from ai_career_advisor.services.backward_roadmap_service import BackwardRoadmapService
            roadmap = await BackwardRoadmapService.get_by_career(db, career_name=career_name)
            
            if not roadmap:
                logger.info(f"📭 No existing roadmap for '{career_name}' - will use RAG/LLM")
                return None
            
            logger.success(f"✅ Found existing roadmap for '{career_name}' in DB!")
            
            # Format short answer with redirect link
            if use_hindi:
                response_text = f"""🎯 **{roadmap.normalized_career} banne ke liye:**

📚 **Education:** {roadmap.career_description[:200] if roadmap.career_description else 'Details available'}...

✨ **Quick Overview:**
- 📝 Exams: {', '.join(roadmap.entrance_exams[:3]) if roadmap.entrance_exams else 'Check feature'}
- 🏫 Top Colleges: {', '.join(roadmap.top_colleges[:3]) if roadmap.top_colleges else 'IITs, NITs'}
- 💰 Salary Range: {roadmap.career_prospects.get('salary_range', 'Competitive') if roadmap.career_prospects else 'Competitive'}

🗺️ **Complete step-by-step roadmap chahiye?**
👉 [Yahan click karein - Career Roadmap](/roadmap/backward)

*Wahan apna personalized roadmap banao with timeline, skills, projects aur more!*"""
            else:
                response_text = f"""🎯 **To become a {roadmap.normalized_career}:**

📚 **Overview:** {roadmap.career_description[:200] if roadmap.career_description else 'Details available in our roadmap generator'}...

✨ **Quick Facts:**
- 📝 Key Exams: {', '.join(roadmap.entrance_exams[:3]) if roadmap.entrance_exams else 'Check feature for details'}
- 🏫 Top Colleges: {', '.join(roadmap.top_colleges[:3]) if roadmap.top_colleges else 'IITs, NITs, top institutes'}
- 💰 Salary Range: {roadmap.career_prospects.get('salary_range', 'Competitive packages') if roadmap.career_prospects else 'Competitive packages'}

🗺️ **Want a detailed step-by-step roadmap?**
👉 [Click here to use our Career Roadmap](/roadmap/backward)

*Get a personalized roadmap with timeline, required skills, projects to build, certifications, and more!*"""
            
            response_time = time.time() - start_time
            
            await ChatbotService._save_conversation(
                db, session_id, user_email, query, response_text,
                "feature_db", 1.0, response_time, ["Career Roadmap Database"]
            )
            
            return {
                "session_id": session_id,
                "query": query,
                "response": response_text,
                "sources": ["Career Roadmap Database", f"Roadmap ID: {roadmap.id}"],
                "confidence": 1.0,
                "response_type": "feature_db",
                "response_time": response_time,
                "feature_redirect": "/roadmap/backward"
            }
            
        except Exception as e:
            logger.error(f"Error checking roadmap DB: {e}")
            return None
    
    @staticmethod
    def _extract_career_from_query(query: str) -> str:
        """Extract career name from query like 'I want to become a software engineer'"""
        import re
        query_lower = query.lower().strip()
        
        # Patterns to match
        patterns = [
            r"(?:i want to become|become|be) (?:a |an )?(.+?)(?:\?|$|\.)",
            r"(?:how to become|kaise bane|kaise banu) (?:a |an )?(.+?)(?:\?|$|\.)",
            r"roadmap (?:for|to become) (?:a |an )?(.+?)(?:\?|$|\.)",
            r"(.+?) (?:banna hai|banna chahta|banna chahti|banana hai)",
            r"career (?:in|as) (?:a |an )?(.+?)(?:\?|$|\.)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                career = match.group(1).strip()
                # Normalize common terms
                career = career.replace("sde", "software engineer")
                career = career.replace("se", "software engineer")
                career = career.replace("ds", "data scientist")
                # Title case for DB matching
                return career.title()
        
        return None

    
    @staticmethod
    async def _safe_rag_search(query: str) -> Dict[str, Any]:
        """
        RAG search with full error handling
        Never raises exceptions - returns empty result on failure
        """
        try:
            from ai_career_advisor.RAG.retriever import retriever
            logger.info("🔍 Searching RAG database...")
            result = await retriever.search_and_build_context(query, top_k=5)
            
            if result["found"]:
                logger.success(f"✅ RAG found {result.get('num_documents', 0)} documents")
            else:
                logger.info("📭 RAG database empty for this query")
            
            return result
        
        except Exception as e:
            logger.warning(f"⚠️ RAG search failed: {str(e)} - using Perplexity fallback")
            return {
                "found": False,
                "context": "",
                "sources": [],
                "scores": [],
                "num_documents": 0
            }
    
    @staticmethod
    async def _generate_with_rag(query: str, context: str, rag_sources: List[str], use_hindi: bool) -> Tuple[str, List[str]]:
        """Generate response using RAG context with Perplexity - returns (text, sources)"""
        PERPLEXITY_API_KEY = settings.PERPLEXITY_API_KEY or ""
        
        if not PERPLEXITY_API_KEY:
            return ("Configuration error. Please contact support.", ["System Error"])
        
        lang_instruction = "Answer in Hindi/Hinglish." if use_hindi else "Answer in English only."
        
        prompt = f"""You are an AI Career Counselor for Indian students. Answer using the verified context below.

VERIFIED DATA:
{context}

QUESTION: {query}

RULES:
- Use ONLY the context above
- {lang_instruction}
- Be concise, under 200 words
- Include specific details (fees, dates, etc.) if available
- Do NOT mix languages unless user asked in mixed language"""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers={
                        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "sonar",
                        "messages": [
                            {"role": "system", "content": f"You are a helpful career counselor. {lang_instruction} Use only the provided context."},
                            {"role": "user", "content": prompt}
                        ]
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data["choices"][0]["message"]["content"].strip()
                    sources = rag_sources if rag_sources else ["Knowledge Base - Verified Data"]
                    return (answer, sources)
                else:
                    logger.error(f"Perplexity API error: {response.status_code}")
                    return await ChatbotService._generate_with_perplexity(query, use_hindi)
        
        except Exception as e:
            logger.error(f"RAG generation error: {e}")
            return await ChatbotService._generate_with_perplexity(query, use_hindi)
    
    @staticmethod
    async def _generate_with_perplexity(query: str, use_hindi: bool) -> Tuple[str, List[str]]:
        """Generate response using Perplexity Sonar with web search - returns (text, sources)"""
        PERPLEXITY_API_KEY = settings.PERPLEXITY_API_KEY or ""
        
        if not PERPLEXITY_API_KEY:
            return ("Configuration error. Please contact support.", ["System Error"])
        
        lang_instruction = "Answer in Hindi/Hinglish." if use_hindi else "Answer in English only. Do not use Hindi words."
        
        prompt = f"""You are an AI Career Counselor for Indian students.

QUESTION: {query}

INSTRUCTIONS:
- Search for current, accurate information about Indian education and careers
- {lang_instruction}
- Provide specific details: fees, eligibility, dates, salary ranges
- Keep response under 250 words
- Be factual and cite official sources with links"""

        try:
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
                            {"role": "system", "content": f"You are an expert Indian education and career counselor. {lang_instruction} Always cite your sources."},
                            {"role": "user", "content": prompt}
                        ]
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data["choices"][0]["message"]["content"].strip()
                    
                    # Extract citations from Perplexity response
                    citations = data.get("citations", [])
                    if citations:
                        sources = citations[:5]
                    else:
                        sources = ["Web Search - Official Sources"]
                    
                    # Add disclaimer
                    answer += "\n\n💡 *Please verify from official sources before making decisions.*"
                    
                    return (answer, sources)
                else:
                    logger.error(f"Perplexity API error: {response.status_code}")
                    return ("I'm having trouble connecting. Please try again.", ["Connection Error"])
        
        except Exception as e:
            logger.error(f"Perplexity error: {e}")
            return ("I'm experiencing technical difficulties. Please try again.", ["Technical Error"])
    
    @staticmethod
    def _detect_features(query: str) -> str:
        """Detect if query relates to a feature and return redirect link"""
        query_lower = query.lower()
        
        for feature_name, feature_config in ChatbotService.FEATURE_PATTERNS.items():
            for keyword in feature_config["keywords"]:
                if keyword in query_lower:
                    logger.info(f"🔗 Feature detected: {feature_name}")
                    return feature_config["message"]
        
        return ""
    
    @staticmethod
    async def _save_to_rag(query: str, response: str, session_id: str):
        """Try to save response to RAG for future use (non-blocking)"""
        try:
            from ai_career_advisor.RAG.retriever import retriever
            await retriever.add_to_knowledge_base(
                query=query,
                response=response,
                metadata={
                    "source": "perplexity_sonar",
                    "session_id": session_id,
                    "timestamp": time.time()
                }
            )
            logger.success("💾 Response saved to RAG")
        except Exception as e:
            logger.warning(f"Could not save to RAG: {e}")
    
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
        """Save conversation to database (non-blocking)"""
        if not db:
            return
        
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
            logger.debug(f"💾 Conversation saved")
        
        except Exception as e:
            logger.warning(f"Could not save conversation: {e}")
            try:
                await db.rollback()
            except:
                pass
