import google.generativeai as genai
from ai_career_advisor.core.config import settings
from ai_career_advisor.core.logger import logger
import asyncio
from functools import partial


genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


class IntentFilter:
    """
    Simple 2-step intent filter:
    1. Check blacklist (instant reject)
    2. Ask LLM if career-related
    """
    
    # Only blocked/inappropriate keywords
    BLACKLIST_KEYWORDS = [
        # Inappropriate content
        "porn", "sex", "nude", "adult", "xxx", "nsfw",
        
        # Entertainment
        "recipe", "weather", "movie", "cricket", "football",
        "joke", "poem", "song", "music", "game", "entertainment",
        "cooking", "biryani", "food", "restaurant", "travel",
        
        # Off-topic
        "news", "politics", "stock market", "cryptocurrency",
        "shopping", "fashion", "beauty", "makeup", "diet",
        "astrology", "horoscope", "zodiac", "dating", "love"
    ]
    
    @staticmethod
    def is_career_related(query: str) -> dict:
        """
        Main intent classification
        Returns: {
            "is_career": bool,
            "confidence": float,
            "method": "blacklist" | "llm",
            "reason": str
        }
        """
        query_lower = query.lower().strip()
        
        # Basic validation
        if len(query_lower) < 3:
            return {
                "is_career": False,
                "confidence": 1.0,
                "method": "validation",
                "reason": "Query too short"
            }
        
        # STEP 1: Check blacklist
        for keyword in IntentFilter.BLACKLIST_KEYWORDS:
            if keyword in query_lower:
                logger.warning(f"Blacklist keyword found: {keyword}")
                return {
                    "is_career": False,
                    "confidence": 1.0,
                    "method": "blacklist",
                    "reason": f"Blocked keyword: {keyword}"
                }
        
        # STEP 2: Ask LLM (no blacklist match, so ask LLM)
        logger.info(f"No blacklist match, asking LLM: {query[:50]}")
        return IntentFilter._llm_classify(query)
    
    @staticmethod
    def _llm_classify(query: str) -> dict:
        """
        LLM decides if query is career/education related
        """
        prompt = f"""You are an intent classifier for an Indian education and career counseling chatbot.

USER QUERY: "{query}"

Is this query related to EDUCATION or CAREER guidance?

CAREER/EDUCATION topics:
- Career choices (any profession: doctor, engineer, IAS, teacher, artist, etc.)
- Educational paths (streams, degrees, colleges, entrance exams)
- Study guidance, skills, preparation, fees, scholarships
- Job prospects, salaries, placements

NOT CAREER/EDUCATION:
- General knowledge, entertainment, sports, cooking, weather
- Personal chitchat unrelated to career

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
                logger.success(f"LLM: Query is career-related")
                return {
                    "is_career": True,
                    "confidence": 0.90,
                    "method": "llm",
                    "reason": "LLM classified as career-related"
                }
            else:
                logger.info(f"LLM: Query is NOT career-related")
                return {
                    "is_career": False,
                    "confidence": 0.90,
                    "method": "llm",
                    "reason": "LLM classified as non-career"
                }
        
        except Exception as e:
            logger.error(f"LLM error: {str(e)}")
            # Failsafe: Allow query if LLM fails
            return {
                "is_career": True,
                "confidence": 0.5,
                "method": "llm_error",
                "reason": "LLM error, allowing query as failsafe"
            }
    
    @staticmethod
    def get_rejection_message() -> dict:
        """User-friendly rejection message"""
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
- "How to become IAS officer?"

Koi career ya education-related question poocho! 😊""",
            "sources": [],
            "confidence": 0.0,
            "responsetype": "rejected"
        }
