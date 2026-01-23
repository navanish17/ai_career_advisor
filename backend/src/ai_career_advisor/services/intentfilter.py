import google.generativeai as genai
from ai_career_advisor.core.config import settings
from ai_career_advisor.core.logger import logger
import asyncio
from functools import partial

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-exp")

class IntentFilter:
    """
    Hybrid intent classification system
    Layer 1: Fast keyword-based filter (0.01 sec)
    Layer 2: LLM-based classifier for edge cases (1-2 sec)
    """
    
    # Career-related keywords (whitelist)
    CAREER_KEYWORDS = [
        "college", "university", "iit", "nit", "aiims", "school", 
        "degree", "btech", "mbbs", "mba", "bsc", "bca", "mca",
        "engineering", "medical", "commerce", "arts", "science",
        
        "engineer", "doctor", "lawyer", "teacher", "developer",
        "software", "mechanical", "civil", "medicine", "nursing",
        "architect", "ca", "chartered accountant", "designer",
        

        "jee", "neet", "cuet", "cat", "gate", "upsc", "exam",
        "entrance", "admission", "cutoff", "rank", "percentile",
        "test", "nta", "counseling",
        
        "career", "job", "salary", "placement", "internship",
        "study", "course", "stream", "subject", "branch",
        "roadmap", "guidance", "counseling", "fees", "scholarship",
        
        "10th", "12th", "class 10", "class 12", "after 10th", "after 12th",
        "graduation", "post graduation", "undergraduate", "masters",
        

        "padhai", "naukri",
        "banna hai", "banne ke liye"
    ]
    
    BLACKLIST_KEYWORDS = [
        "recipe", "weather", "movie", "cricket", "football",
        "joke", "poem", "song", "music", "game", "entertainment",
        "cooking", "biryani", "food", "restaurant", "travel",
        "news", "politics", "stock market", "cryptocurrency"
    ]
    
    @staticmethod
    def is_career_related(query: str) -> dict:
        """
        Main intent classification function
        Returns: {
            "is_career": bool,
            "confidence": float,
            "method": "keyword" | "llm",
            "reason": str
        }
        """
        query_lower = query.lower().strip()
        
        if len(query_lower) < 3:
            return {
                "is_career": False,
                "confidence": 1.0,
                "method": "validation",
                "reason": "Query too short"
            }
        
        keyword_result = IntentFilter._keyword_check(query_lower)
        
        if keyword_result["decision"] == "accept":
            return {
                "is_career": True,
                "confidence": 0.95,
                "method": "keyword",
                "reason": f"Career keyword found: {keyword_result['matched_keyword']}"
            }
        
        if keyword_result["decision"] == "reject":
            return {
                "is_career": False,
                "confidence": 0.95,
                "method": "keyword",
                "reason": f"Blacklist keyword found: {keyword_result['matched_keyword']}"
            }
        
       
        logger.info(f"Keyword unsure, using LLM for: {query[:50]}")
        return IntentFilter._llm_classify(query)
    
    @staticmethod
    def _keyword_check(query_lower: str) -> dict:
        """
        Fast keyword-based check
        Returns: {"decision": "accept" | "reject" | "unsure", "matched_keyword": str}
        """

        for keyword in IntentFilter.CAREER_KEYWORDS:
            if keyword in query_lower:
                return {
                    "decision": "accept",
                    "matched_keyword": keyword
                }
        
        
        for keyword in IntentFilter.BLACKLIST_KEYWORDS:
            if keyword in query_lower:
                return {
                    "decision": "reject",
                    "matched_keyword": keyword
                }
        
        
        return {
            "decision": "unsure",
            "matched_keyword": None
        }
    
    @staticmethod
    def _llm_classify(query: str) -> dict:
        """
        LLM-based intent classification for edge cases
        """
        prompt = f"""You are an intent classifier. Classify this user query as CAREER or NON_CAREER.

CAREER = Questions about education, colleges, exams, jobs, degrees, streams, career paths, salary, courses, counseling, guidance
NON_CAREER = Everything else (cooking, weather, entertainment, general knowledge, jokes, poems, etc.)

USER QUERY: {query}

Reply with ONLY one word: CAREER or NON_CAREER"""

        try:
            loop = asyncio.get_event_loop()
            response = loop.run_until_complete(
                loop.run_in_executor(
                    None,
                    partial(model.generate_content, prompt)
                )
            )
            
            intent = response.text.strip().upper()
            
            if "CAREER" in intent:
                return {
                    "is_career": True,
                    "confidence": 0.90,
                    "method": "llm",
                    "reason": "LLM classified as career-related"
                }
            else:
                return {
                    "is_career": False,
                    "confidence": 0.90,
                    "method": "llm",
                    "reason": "LLM classified as non-career"
                }
        
        except Exception as e:
            logger.error(f"LLM classification error: {str(e)}")
            
            return {
                "is_career": False,
                "confidence": 0.5,
                "method": "llm_error",
                "reason": f"LLM error: {str(e)}"
            }
    
    @staticmethod
    def get_rejection_message() -> dict:
        """
        User-friendly rejection message
        """
        return {
            "response": """🎓 Main ek **AI Career Counselor** hoon for Indian students!

**Main tumhari help kar sakta hoon:**
✅ Career guidance (after 10th/12th)
✅ College selection (IITs, NITs, top colleges)
✅ Entrance exams (JEE, NEET, CUET, etc.)
✅ Career roadmaps (Software Engineer, Doctor, CA, etc.)
✅ Salary & job prospects

**Try asking:**
- "Software engineer kaise bane?"
- "IIT Delhi CSE cutoff kya hai?"
- "What after 12th Science?"
- "JEE Main ke liye preparation kaise kare?"

Koi career ya education-related question poocho! 😊""",
            "sources": [],
            "confidence": 0.0,
            "responsetype": "rejected"
        }
