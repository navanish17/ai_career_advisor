import google.generativeai as genai
from ai_career_advisor.core.config import settings
from ai_career_advisor.core.logger import logger  # ✅ Your logger
from google.api_core.exceptions import ResourceExhausted, GoogleAPIError
import asyncio
from functools import partial

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash-lite")

class CollegeProgramCheckService:
    @staticmethod
    async def check(*, college_name: str, degree: str, branch: str) -> bool:
        """
        Fast yes/no check using Gemini
        """
        prompt = f"""Answer ONLY true or false (single word).
Does {college_name} offer {degree} in {branch} branch?
Rules: Reply ONLY: true OR false. If unsure: false."""

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                partial(model.generate_content, prompt)
            )
            
            answer = response.text.strip().lower()
            result = "true" in answer
            
            if result:
                logger.debug(f"   ✅ {college_name} offers {degree} {branch}")
            else:
                logger.debug(f"   ❌ {college_name} does NOT offer {degree} {branch}")
            
            return result

        except (ResourceExhausted, GoogleAPIError, Exception) as e:
            logger.error(f"   🔴 Error checking {college_name}: {e}")
            return False
