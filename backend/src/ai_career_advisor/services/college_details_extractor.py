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
You are a STRICT data extraction engine that ONLY extracts explicitly stated information.

CORE PRINCIPLES:
- Extract ONLY what is directly written in the source
- DO NOT guess, infer, calculate, or approximate
- DO NOT fabricate any data
- If information is not found, return "Not available"

TARGET EXTRACTION:
College: {college_name}
Degree: {degree}
Branch: {branch}

NOTE: Extract data ONLY for the degree and branch specified above. Do not use data from other degrees or branches.

SOURCE PRIORITY (use in this order):
1. Official .ac.in / .edu.in domains or their PDFs
2. Shiksha.com
3. Careers360.com
4. CollegeDunia.com
* no extra source other than this 

DATA FIELDS TO EXTRACT:
1. Annual tuition fees (exclude hostel/mess fees)
2. Average placement package (branch-specific preferred)
3. Highest placement package (branch-specific preferred)
4. Entrance exam name
5. Cutoff (rank/percentile with year and category)

EXTRACTION RULES:
✓ Use most recent data (2024-25 or 2025-26 preferred)
✓ If branch-specific placement data unavailable, use overall degree data and mention note: "Overall degree data used". if doing then only if found branch related then avoid note*. 
✓ Copy exact sentences from source as extracted_text
✓ Include exact source URL for each field

✗ DO NOT mix data from different degrees or branches
✗ DO NOT use outdated data if recent data exists
✗ DO NOT perform calculations or estimations
✗ DO NOT add fabricated years or values

OUTPUT FORMAT:
i want datain this form only {{
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

VERIFICATION CHECKLIST:
Before returning output, verify:
□ All values are directly quoted from sources
□ All sources are valid URLs
□ No data is mixed from other degrees/branches
□ No calculations or approximations made
□ JSON only
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