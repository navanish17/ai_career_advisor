import json
import google.generativeai as genai
from ai_career_advisor.core.config import settings
from ai_career_advisor.core.logger import logger
import asyncio
from functools import partial
from google.api_core.exceptions import ResourceExhausted, GoogleAPIError


genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash-lite")


class CareerNormalizerService:
    """
    Normalizes and validates user career input
    Converts variations to standard career names
    """
    
    @staticmethod
    async def normalize_and_validate(user_input: str) -> dict:
        """
        Validates and normalizes career goal input
        
        Args:
            user_input: Raw user input (e.g., "software developer", "doctor", "I want to code")
        
        Returns:
            {
                "is_valid": True/False,
                "normalized_career": "Software Engineer" or None,
                "category": "Technology" or None,
                "confidence": 0.0-1.0,
                "reason": "Explanation if invalid"
            }
        """
        
        logger.info(f"🔍 Normalizing career input: '{user_input}'")
        
        # Quick validation
        if not user_input or len(user_input.strip()) < 3:
            logger.warning(f"   ❌ Input too short")
            return {
                "is_valid": False,
                "normalized_career": None,
                "category": None,
                "confidence": 0.0,
                "reason": "Career goal is too short. Please provide a specific career name."
            }
        
        prompt = f"""
You are a career normalization and validation engine for an Indian career counseling platform.

USER INPUT: "{user_input}"

TASK:
1. Determine if this is a VALID, SPECIFIC career goal
2. Convert to a standard career name (Indian context)
3. Categorize the career
4. Provide confidence score

VALID careers: Any recognized profession in India
Examples: Software Engineer, Doctor, CA, IAS Officer, Teacher, Graphic Designer, etc.

INVALID inputs:
- Vague goals: "earn money", "be successful", "be happy"
- Incomplete: "xyz", "abc", random text
- Questions: "what should I do?"

RETURN ONLY VALID JSON (no markdown, no explanation):

{{
  "is_valid": true or false,
  "normalized_career": "Standard Career Name" or null,
  "category": "Technology/Healthcare/Government/Business/Engineering/Arts/Education/Legal/etc" or null,
  "confidence": 0.0-1.0,
  "reason": "Brief explanation if invalid, otherwise null"
}}

EXAMPLES:

Input: "software developer"
Output: {{"is_valid": true, "normalized_career": "Software Engineer", "category": "Technology", "confidence": 0.95, "reason": null}}

Input: "doctor"
Output: {{"is_valid": true, "normalized_career": "Medical Doctor", "category": "Healthcare", "confidence": 1.0, "reason": null}}

Input: "CA"
Output: {{"is_valid": true, "normalized_career": "Chartered Accountant", "category": "Business", "confidence": 0.9, "reason": null}}

Input: "IAS"
Output: {{"is_valid": true, "normalized_career": "IAS Officer", "category": "Government", "confidence": 0.95, "reason": null}}

Input: "data scientist"
Output: {{"is_valid": true, "normalized_career": "Data Scientist", "category": "Technology", "confidence": 0.95, "reason": null}}

Input: "i want to code"
Output: {{"is_valid": false, "normalized_career": null, "category": null, "confidence": 0.0, "reason": "Not a specific career. Did you mean Software Engineer or Web Developer?"}}

Input: "earn lots of money"
Output: {{"is_valid": false, "normalized_career": null, "category": null, "confidence": 0.0, "reason": "Not a career goal. Please specify a profession (e.g., Doctor, Engineer, Lawyer)."}}

Input: "xyz"
Output: {{"is_valid": false, "normalized_career": null, "category": null, "confidence": 0.0, "reason": "Unrecognized input. Please provide a valid career name."}}

NOW PROCESS: "{user_input}"
"""
        
        try:
            # Call Gemini API
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    partial(model.generate_content, prompt)
                ),
                timeout=30.0
            )
            
            text = response.text.strip()
            
            # Clean markdown
            if text.startswith("```"):
                text = text.replace("```json", "").replace("```", "").strip()
            
            # Parse JSON
            result = json.loads(text)
            
            # Log result
            if result.get("is_valid"):
                logger.success(f"   ✅ Normalized: '{user_input}' → '{result['normalized_career']}' ({result['category']})")
            else:
                logger.warning(f"   ❌ Invalid career: {result.get('reason')}")
            
            return result
        
        except asyncio.TimeoutError:
            logger.error(f"   ⏱️ Timeout normalizing '{user_input}'")
            return {
                "is_valid": False,
                "normalized_career": None,
                "category": None,
                "confidence": 0.0,
                "reason": "Request timeout. Please try again."
            }
        
        except (ResourceExhausted, GoogleAPIError) as e:
            logger.error(f"    API Error: {str(e)}")
            return {
                "is_valid": False,
                "normalized_career": None,
                "category": None,
                "confidence": 0.0,
                "reason": "Service temporarily unavailable. Please try again."
            }
        
        except json.JSONDecodeError as e:
            logger.error(f"    JSON parse error: {str(e)}")
            logger.error(f"   Raw response: {text[:200]}")
            return {
                "is_valid": False,
                "normalized_career": None,
                "category": None,
                "confidence": 0.0,
                "reason": "Error processing request. Please try again."
            }
        
        except Exception as e:
            logger.error(f"    Unexpected error: {str(e)}")
            return {
                "is_valid": False,
                "normalized_career": None,
                "category": None,
                "confidence": 0.0,
                "reason": "Unexpected error. Please try again."
            }
