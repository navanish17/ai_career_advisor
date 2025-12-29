import json
import google.generativeai as genai
from ai_career_advisor.core.config import settings
import asyncio
from functools import partial
from google.api_core.exceptions import ResourceExhausted, GoogleAPIError

genai.configure(api_key=settings.GEMINI_API_KEY)

# ✅ Model correct hai
model = genai.GenerativeModel("gemini-2.5-flash-lite")

class CollegeStrictGeminiExtractor:
    @staticmethod
    async def extract(*, college_name: str, degree: str, branch: str) -> dict:
        
        prompt = f"""
You are a STRICT data extraction engine.

DO NOT GUESS. DO NOT INFER. DO NOT ASSUME.
ONLY extract information that is EXPLICITLY written in the content.

COLLEGE: {college_name}
DEGREE: {degree}
BRANCH: {branch}

SOURCE PRIORITY (highest → lowest):
1. Official .ac.in / .edu.in websites or PDFs
2. Shiksha.com
3. Careers360.com
4. CollegeDunia.com

EXTRACT DATA FOR ONLY:
→ Degree: {degree}
→ Branch: {branch}

FIELDS TO EXTRACT:
1. Annual tuition fees
2. Average placement package (branch-specific if available)
3. Highest placement package (branch-specific if available)
4. Entrance exam name
5. Cutoff (rank / percentile with year & category)

STRICT RULES:
❌ Do NOT use data of other degrees
❌ Do NOT use data of other branches
❌ If branch-specific data NOT found → use overall degree data AND clearly say so
❌ Do NOT mix hostel/mess fees with tuition fees
❌ Do NOT calculate or approximate
❌ Do NOT fabricate years or values
❌ If 2024–25 or 2025–26 exists, ignore older data
❌ If ANY verification fails → return "Not available"

MANDATORY:
Every extracted field MUST include:
- exact copied sentence (extracted_text)
- exact source URL

RETURN STRICT JSON ONLY (no text, no explanation):

{{
  "college_name": "{college_name}",
  "degree": "{degree}",
  "branch": "{branch}",

  "fees": {{
    "value": "₹X per year OR Not available",
    "source": "exact URL OR null",
    "extracted_text": "exact sentence copied from source OR null"
  }},

  "avg_package": {{
    "value": "X LPA OR Not available",
    "source": "exact URL OR null",
    "extracted_text": "exact sentence copied from source OR null"
  }},

  "highest_package": {{
    "value": "X LPA OR Not available",
    "source": "exact URL OR null",
    "extracted_text": "exact sentence copied from source OR null"
  }},

  "entrance_exam": {{
    "value": "Exam name OR Not available",
    "source": "exact URL OR null",
    "extracted_text": "exact sentence copied from source OR null"
  }},

  "cutoff": {{
    "value": "Rank/percentile (year, category) OR Not available",
    "source": "exact URL OR null",
    "extracted_text": "exact sentence copied from source OR null"
  }}
}}

IMPORTANT:
- Output ONLY valid JSON
- No markdown
- No comments
"""

        # 🔹 Retry logic
        max_retries = 3
        base_delay = 5  # Extraction takes longer, so more gap

        for attempt in range(max_retries):
            try:
                # ✅ Delay between requests (Free tier: 15 RPM = 4s gap minimum)
                await asyncio.sleep(5)  # Safe gap for rate limits
                
                if attempt > 0:
                    delay = base_delay * (2 ** attempt)
                    print(f"🟡 Retry {attempt + 1} for {college_name} extraction after {delay}s")
                    await asyncio.sleep(delay)
                
                # ✅ Async executor with longer timeout
                loop = asyncio.get_event_loop()
                response = await asyncio.wait_for(
                    loop.run_in_executor(
                        None,
                        partial(model.generate_content, prompt)
                    ),
                    timeout=120.0  # 2 minute timeout (extraction takes time)
                )
                
                text = response.text.strip()

                # Remove markdown fences if present
                if text.startswith("```"):
                    text = text.replace("```json", "").replace("```", "")

                # Safe JSON parsing
                try:
                    return json.loads(text)
                except Exception as e:
                    print(f"🔴 JSON parse error for {college_name}: {str(e)}")
                    return {
                        "error": "Invalid JSON returned by Gemini",
                        "raw_response": text
                    }

            except asyncio.TimeoutError:
                print(f"⏱️ Timeout extracting {college_name} (attempt {attempt + 1})")
                if attempt == max_retries - 1:
                    return {"error": "timeout_exceeded"}
                continue

            except ResourceExhausted:
                print(f"🟡 Rate limit during extraction for {college_name}")
                await asyncio.sleep(60)  # Wait 1 minute
                if attempt == max_retries - 1:
                    return {"error": "quota_exhausted"}
                continue
            
            except GoogleAPIError as e:
                print(f"🔴 API Error for {college_name}: {str(e)}")
                return {"error": f"api_error: {str(e)}"}
            
            except Exception as e:
                print(f"🔴 Unexpected error for {college_name}: {str(e)}")
                return {"error": f"unexpected: {str(e)}"}

        return {"error": "all_retries_failed"}