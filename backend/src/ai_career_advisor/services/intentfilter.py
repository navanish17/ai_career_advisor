from ai_career_advisor.core.config import settings
from ai_career_advisor.core.logger import logger
import httpx
import asyncio


class IntentFilter:
    """
    Simple 3-step intent filter:
    1. Check greetings (instant accept with friendly response)
    2. Check blacklist (instant reject)
    3. Use simple keyword matching for career topics
    """
    
    # Greetings that should get a friendly response
    GREETINGS = [
        "hi", "hello", "hey", "namaste", "hii", "helo", "hola",
        "good morning", "good afternoon", "good evening",
        "kaise ho", "how are you", "what's up", "sup"
    ]
    
    # Career/Education keywords (if ANY found, it's career-related)
    CAREER_KEYWORDS = [
        # Education
        "college", "university", "iit", "nit", "aiims", "school", "degree",
        "btech", "bsc", "mba", "mbbs", "engineering", "medical", "commerce",
        "science", "arts", "diploma", "phd", "masters", "bachelor",
        
        # Exams
        "jee", "neet", "gate", "cat", "upsc", "ssc", "exam", "entrance",
        "cuet", "clat", "nda", "cds", "ias", "ips", "test", "cutoff",
        
        # Career
        "career", "job", "salary", "placement", "package", "internship",
        "engineer", "doctor", "teacher", "lawyer", "ca", "cs", "software",
        "developer", "data scientist", "analyst", "manager", "consultant",
        
        # Guidance
        "course", "stream", "branch", "admission", "eligibility", "fees",
        "scholarship", "counseling", "guidance", "roadmap", "preparation",
        "study", "skill", "training", "certification", "after 10th", "after 12th"
    ]
    
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
            "method": "greeting" | "blacklist" | "keyword" | "default",
            "reason": str
        }
        """
        query_lower = query.lower().strip()
        
        # Basic validation
        if len(query_lower) < 2:
            return {
                "is_career": False,
                "confidence": 1.0,
                "method": "validation",
                "reason": "Query too short"
            }
        
        # STEP 1: Check if it's a greeting
        for greeting in IntentFilter.GREETINGS:
            if query_lower == greeting or query_lower.startswith(greeting + " "):
                logger.info(f"✋ Greeting detected: {greeting}")
                return {
                    "is_career": True,  # Allow greetings to pass through
                    "confidence": 1.0,
                    "method": "greeting",
                    "reason": "Greeting detected",
                    "is_greeting": True  # Special flag
                }
        
        # STEP 2: Check blacklist
        for keyword in IntentFilter.BLACKLIST_KEYWORDS:
            if keyword in query_lower:
                logger.warning(f"🚫 Blacklist keyword found: {keyword}")
                return {
                    "is_career": False,
                    "confidence": 1.0,
                    "method": "blacklist",
                    "reason": f"Blocked keyword: {keyword}"
                }
        
        # STEP 3: Check career keywords
        for keyword in IntentFilter.CAREER_KEYWORDS:
            if keyword in query_lower:
                logger.success(f"✅ Career keyword found: {keyword}")
                return {
                    "is_career": True,
                    "confidence": 0.95,
                    "method": "keyword",
                    "reason": f"Career keyword: {keyword}"
                }
        
        # STEP 4: Default - allow it (better to answer than reject)
        logger.info(f"🤔 No clear match, allowing query as potential career question")
        return {
            "is_career": True,
            "confidence": 0.6,
            "method": "default",
            "reason": "No blacklist match, allowing as potential career query"
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
    
    @staticmethod
    def get_greeting_response() -> str:
        """Friendly greeting response"""
        return """👋 **Hello! Main aapka AI Career Counselor hoon!**

Main Indian students ko career aur education guidance deta hoon. 

**Aap mujhse puch sakte ho:**
💼 Career options (Engineering, Medical, Commerce, Arts)
🎓 College selection (IITs, NITs, private colleges)
📝 Entrance exams (JEE, NEET, CUET, CAT, etc.)
💰 Fees, placements, salaries
📚 Study tips aur roadmaps

**Kuch examples:**
- "12th ke baad kya kare?"
- "IIT mein admission kaise le?"
- "Software engineer ka salary kitna hai?"

Apna question poocho! 😊"""
