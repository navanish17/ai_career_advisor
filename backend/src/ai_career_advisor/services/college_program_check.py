import google.generativeai as genai
from ai_career_advisor.core.config import settings
from google.api_core.exceptions import ResourceExhausted, GoogleAPIError
import asyncio
from functools import partial

genai.configure(api_key=settings.GEMINI_API_KEY)

# ✅ Model sahi hai
model = genai.GenerativeModel("gemini-2.5-flash-lite")

class CollegeProgramCheckService:
    @staticmethod
    async def check(*, college_name: str, degree: str, branch: str) -> bool:
        prompt = f"""Answer ONLY true or false.
Does {college_name} offer {degree} in {branch}?
Rules: No explanation. If unsure, return false."""

        # 🔹 Retry logic with exponential backoff
        max_retries = 3
        base_delay = 2  # seconds

        for attempt in range(max_retries):
            try:
                # ✅ Free tier ke liye delay (15 RPM = 4 seconds gap)
                if attempt > 0:
                    delay = base_delay * (2 ** attempt)  # 2, 4, 8 seconds
                    print(f"🟡 Retry {attempt + 1} for {college_name} after {delay}s")
                    await asyncio.sleep(delay)
                
                # ✅ Async executor with timeout
                loop = asyncio.get_event_loop()
                response = await asyncio.wait_for(
                    loop.run_in_executor(
                        None, 
                        partial(model.generate_content, prompt)
                    ),
                    timeout=60.0  # 60 second timeout
                )
                
                answer = response.text.strip().lower()
                return "true" in answer

            except asyncio.TimeoutError:
                print(f"⏱️ Timeout for {college_name} (attempt {attempt + 1})")
                if attempt == max_retries - 1:
                    return False  # Final attempt failed
                continue

            except ResourceExhausted:
                print(f"🟡 Rate limit hit for {college_name}, waiting...")
                await asyncio.sleep(60)  # Wait 1 minute
                if attempt == max_retries - 1:
                    return False
                continue

            except GoogleAPIError as e:
                print(f"🔴 API Error for {college_name}: {str(e)}")
                return False
            
            except Exception as e:
                print(f"🔴 Unexpected error for {college_name}: {str(e)}")
                return False

        return False  # All retries failed
