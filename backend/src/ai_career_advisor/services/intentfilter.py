"""
ML-Based Intent Filter using BERT Classifier

📚 STUDY NOTES - HOW THIS IMPROVES OVER RULE-BASED:
==================================================

BEFORE (Rule-Based):
- Hard-coded keyword lists
- No understanding of context
- "best iit" works, but "top engineering institutes" fails
- Manual maintenance required

AFTER (ML-Based):
- Learns patterns from data
- Understands semantics (similar meanings)
- "best iit" AND "top engineering institutes" both work
- Improves with more training data

📚 INTERVIEW QUESTION: "Why use ML instead of rules?"
Answer: "Rules are brittle and don't generalize. The ML model learns 
semantic representations, so 'best IIT' and 'top engineering college' 
are understood as similar queries even though they use different words."
"""

from ai_career_advisor.core.config import settings
from ai_career_advisor.core.logger import logger
from typing import Dict, Any, Optional
import os
from pathlib import Path


# Track whether ML model is available
_ml_model_available = False
_intent_classifier = None


def _load_ml_model():
    """
    Lazy load the ML model
    
    📚 STUDY NOTE - Why Lazy Loading?
    - Model is large (100+ MB)
    - Loading takes time (1-2 seconds)
    - Only load when first needed
    - Faster server startup
    """
    global _ml_model_available, _intent_classifier
    
    try:
        from ai_career_advisor.ml_models.intent_classifier import get_intent_classifier
        model_path = Path(__file__).parent.parent / "models" / "intent_classifier"
        
        if model_path.exists():
            _intent_classifier = get_intent_classifier()
            _ml_model_available = True
            logger.info("✅ ML Intent Classifier loaded successfully")
        else:
            logger.warning("⚠️ No trained ML model found, using rule-based fallback")
            _ml_model_available = False
    except Exception as e:
        logger.error(f"❌ Failed to load ML model: {e}")
        _ml_model_available = False


class IntentFilterML:
    """
    Hybrid Intent Filter with ML and Rule-based fallback
    
    📚 INTERVIEW TALKING POINT:
    "I built a hybrid intent classification system. The primary classifier is 
    a fine-tuned DistilBERT model, but I also have rule-based fallbacks for 
    edge cases and as a safety net. This ensures 100% availability even if 
    the ML model fails to load."
    
    Architecture:
    ┌───────────────┐
    │ User Query    │
    └───────┬───────┘
            │
            ▼
    ┌───────────────┐     ┌─────────────────┐
    │ ML Classifier │────►│ High Confidence │──► Return ML Result
    │ (DistilBERT)  │     │ (> 0.7)         │
    └───────┬───────┘     └─────────────────┘
            │
            ▼ Low Confidence
    ┌───────────────┐
    │ Rule Fallback │────► Return Rule Result
    │ (Keywords)    │
    └───────────────┘
    """
    
    # Greetings that should get a friendly response
    GREETINGS = [
        "hi", "hello", "hey", "namaste", "hii", "helo", "hola",
        "good morning", "good afternoon", "good evening",
        "kaise ho", "how are you", "what's up", "sup"
    ]
    
    # Inappropriate content blocklist
    BLACKLIST_KEYWORDS = [
        "porn", "sex", "nude", "adult", "xxx", "nsfw",
    ]
    
    # ML intent to career-related mapping
    CAREER_INTENTS = [
        "career_query",
        "college_query", 
        "roadmap_request",
        "exam_query",
        "degree_query",
        "recommendation_request"
    ]
    
    NON_CAREER_INTENTS = ["off_topic"]
    
    @staticmethod
    def is_career_related(query: str) -> Dict[str, Any]:
        """
        Main intent classification using ML model with rule-based fallback
        
        Returns: {
            "is_career": bool,
            "confidence": float,
            "method": "ml" | "greeting" | "blacklist" | "keyword" | "default",
            "reason": str,
            "intent": str (optional, only with ML)
        }
        """
        global _ml_model_available, _intent_classifier
        
        query_lower = query.lower().strip()
        
        # Basic validation
        if len(query_lower) < 2:
            return {
                "is_career": False,
                "confidence": 1.0,
                "method": "validation",
                "reason": "Query too short"
            }
        
        # STEP 1: Check for greetings (quick check before ML)
        for greeting in IntentFilterML.GREETINGS:
            if query_lower == greeting or query_lower.startswith(greeting + " "):
                logger.info(f"✋ Greeting detected: {greeting}")
                return {
                    "is_career": True,
                    "confidence": 1.0,
                    "method": "greeting",
                    "reason": "Greeting detected",
                    "is_greeting": True,
                    "intent": "greeting"
                }
        
        # STEP 2: Check blacklist (safety check)
        for keyword in IntentFilterML.BLACKLIST_KEYWORDS:
            if keyword in query_lower:
                logger.warning(f"🚫 Blacklist keyword found: {keyword}")
                return {
                    "is_career": False,
                    "confidence": 1.0,
                    "method": "blacklist",
                    "reason": f"Blocked keyword: {keyword}",
                    "intent": "blocked"
                }
        
        # STEP 3: Try ML classification
        if not _ml_model_available and _intent_classifier is None:
            _load_ml_model()
        
        if _ml_model_available and _intent_classifier is not None:
            try:
                intent, confidence = _intent_classifier.predict(query)
                
                logger.info(f"🤖 ML prediction: {intent} ({confidence:.2%})")
                
                # High confidence ML prediction
                if confidence >= 0.7:
                    is_career = intent in IntentFilterML.CAREER_INTENTS
                    is_greeting = intent == "greeting"
                    is_farewell = intent == "farewell"
                    
                    return {
                        "is_career": is_career or is_greeting or is_farewell,
                        "confidence": confidence,
                        "method": "ml",
                        "reason": f"ML classified as {intent}",
                        "intent": intent,
                        "is_greeting": is_greeting,
                        "is_farewell": is_farewell
                    }
                else:
                    # Low confidence - fall through to rule-based
                    logger.info(f"⚠️ ML confidence low ({confidence:.2%}), using rules")
                    
            except Exception as e:
                logger.error(f"❌ ML prediction failed: {e}")
        
        # STEP 4: Rule-based fallback (same as original IntentFilter)
        return IntentFilterML._rule_based_check(query_lower)
    
    @staticmethod
    def _rule_based_check(query_lower: str) -> Dict[str, Any]:
        """Rule-based fallback classification"""
        
        CAREER_KEYWORDS = [
            "college", "university", "iit", "nit", "aiims", "school", "degree",
            "btech", "bsc", "mba", "mbbs", "engineering", "medical", "commerce",
            "science", "arts", "diploma", "phd", "masters", "bachelor",
            "jee", "neet", "gate", "cat", "upsc", "ssc", "exam", "entrance",
            "cuet", "clat", "nda", "cds", "ias", "ips", "test", "cutoff",
            "career", "job", "salary", "placement", "package", "internship",
            "engineer", "doctor", "teacher", "lawyer", "ca", "cs", "software",
            "developer", "data scientist", "analyst", "manager", "consultant",
            "course", "stream", "branch", "admission", "eligibility", "fees",
            "scholarship", "counseling", "guidance", "roadmap", "preparation",
            "study", "skill", "training", "certification", "after 10th", "after 12th"
        ]
        
        for keyword in CAREER_KEYWORDS:
            if keyword in query_lower:
                logger.info(f"✅ Rule matched keyword: {keyword}")
                return {
                    "is_career": True,
                    "confidence": 0.85,
                    "method": "keyword",
                    "reason": f"Career keyword: {keyword}",
                    "intent": "career_query"
                }
        
        # Default - allow (better to answer than reject)
        logger.info(f"🤔 No clear match, allowing as potential career query")
        return {
            "is_career": True,
            "confidence": 0.5,
            "method": "default",
            "reason": "No blacklist match, allowing as potential career query",
            "intent": "unknown"
        }
    
    @staticmethod
    def get_intent_details(query: str) -> Dict[str, Any]:
        """
        Get detailed intent information including all probabilities
        
        📚 USE IN INTERVIEW DEMO:
        Show this to explain how the model works - it gives probabilities
        for ALL intents, not just the top one.
        """
        global _ml_model_available, _intent_classifier
        
        if not _ml_model_available:
            _load_ml_model()
        
        if _ml_model_available and _intent_classifier is not None:
            try:
                return _intent_classifier.get_detailed_prediction(query)
            except Exception as e:
                logger.error(f"Failed to get detailed prediction: {e}")
        
        # Fallback
        return {
            "text": query,
            "predicted_intent": "unknown",
            "confidence": 0.0,
            "all_probabilities": {},
            "model_available": False
        }
    
    @staticmethod
    def get_rejection_message() -> dict:
        """User-friendly rejection message"""
        return {
            "response": """🎓 I'm an **AI Career Counselor** for Indian students!

**I can help you with:**
✅ Career guidance (after 10th/12th)
✅ College selection (IITs, NITs, top colleges)
✅ Entrance exams (JEE, NEET, CUET, etc.)
✅ Career roadmaps (Software Engineer, Doctor, CA, etc.)
✅ Salary & job prospects

**Try asking:**
- "How to become a software engineer?"
- "Best IIT colleges in India?"
- "What after 12th Science?"
- "How to become IAS officer?"

Ask any career or education-related question! 😊""",
            "sources": [],
            "confidence": 0.0,
            "responsetype": "rejected"
        }
    
    @staticmethod
    def get_greeting_response(use_hindi: bool = False) -> str:
        """Friendly greeting response"""
        if use_hindi:
            return """👋 **Namaste! Main aapka AI Career Counselor hoon!**

Main Indian students ko career aur education guidance deta hoon. 

**Aap mujhse puch sakte ho:**
💼 Career options (Engineering, Medical, Commerce, Arts)
🎓 College selection (IITs, NITs, private colleges)
📝 Entrance exams (JEE, NEET, CUET, CAT, etc.)
💰 Fees, placements, salaries
📚 Study tips aur roadmaps

Apna question poocho! 😊"""
        
        return """👋 **Hello! I'm your AI Career Counselor!**

I help Indian students with career and education guidance.

**You can ask me about:**
💼 Career options (Engineering, Medical, Commerce, Arts)
🎓 College selection (IITs, NITs, private colleges)
📝 Entrance exams (JEE, NEET, CUET, CAT, etc.)
💰 Fees, placements, salaries
📚 Study tips and roadmaps

Ask your question! 😊"""


# Backward compatibility alias
IntentFilter = IntentFilterML
