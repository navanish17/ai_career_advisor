import json
import google.generativeai as genai
from ai_career_advisor.core.config import settings
import asyncio
from functools import partial
from google.api_core.exceptions import ResourceExhausted, GoogleAPIError
from ai_career_advisor.core.logger import logger  # ✅ Your logger

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash-lite")


class CollegeStrictGeminiExtractor:
    
    @staticmethod
    def _is_data_complete(extracted: dict) -> tuple[bool, list]:
        """
        Check if ALL critical fields have valid data
        Returns: (is_complete, missing_fields)
        """
        critical_fields = ["fees", "avg_package", "highest_package", "entrance_exam", "cutoff"]
        missing = []
        
        for field in critical_fields:
            if field not in extracted:
                missing.append(field)
                continue
            
            value = extracted[field].get("value", "")
            
            # Check if value is null, empty, or "Not available"
            if (not value or 
                value.strip() == "" or 
                value.strip().lower() == "not available" or 
                value.strip().lower() == "null"):
                missing.append(field)
        
        return (len(missing) == 0, missing)

    @staticmethod
    async def extract(
        *,
        college_name: str,
        degree: str,
        branch: str,
    ) -> dict:
        """
        Extract college details with retry logic
        """
        
        MAX_RETRIES = 3
        base_delay = 5
        
        for attempt in range(1, MAX_RETRIES + 1):
            
            # =============================
            # LOG: ATTEMPT START
            # =============================
            if attempt == 1:
                logger.info(f"📊 [Attempt {attempt}/{MAX_RETRIES}] Fetching details for {college_name}")
            else:
                logger.warning(f"🔄 [Attempt {attempt}/{MAX_RETRIES}] Retrying due to incomplete data for {college_name}")
            
            # =============================
            # PROMPT (Progressive Relaxation)
            # =============================
            if attempt == 1:
                prompt = f"""
You are a STRICT data extraction engine.

DO NOT GUESS. DO NOT INFER. ONLY extract EXPLICIT information.

COLLEGE: {college_name}
DEGREE: {degree}
BRANCH: {branch}

SEARCH PRIORITY:
1. Official {college_name} website (.ac.in / .edu.in)
2. Shiksha.com
3. Careers360.com
4. CollegeDunia.com

EXTRACT FOR {degree} in {branch}:

MANDATORY FIELDS (ALL REQUIRED):
1. Annual tuition fees (NOT hostel)
2. Average placement package
3. Highest placement package
4. Entrance exam name
5. Cutoff (rank/percentile with year)

RULES:
❌ NO other degree/branch data
❌ Prefer 2024-25 or 2025-26 data
❌ If ANY field unavailable → return "Not available"

RETURN VALID JSON:

{{
  "college_name": "{college_name}",
  "degree": "{degree}",
  "branch": "{branch}",
  
  "fees": {{
    "value": "₹X per year OR Not available",
    "source": "URL OR null",
    "extracted_text": "sentence OR null"
  }},
  
  "avg_package": {{
    "value": "X LPA OR Not available",
    "source": "URL OR null",
    "extracted_text": "sentence OR null"
  }},
  
  "highest_package": {{
    "value": "X LPA OR Not available",
    "source": "URL OR null",
    "extracted_text": "sentence OR null"
  }},
  
  "entrance_exam": {{
    "value": "Exam name OR Not available",
    "source": "URL OR null",
    "extracted_text": "sentence OR null"
  }},
  
  "cutoff": {{
    "value": "Rank (year, category) OR Not available",
    "source": "URL OR null",
    "extracted_text": "sentence OR null"
  }}
}}
"""
            
            elif attempt == 2:
                prompt = f"""
RETRY ATTEMPT: Previous data was incomplete.

COLLEGE: {college_name}
DEGREE: {degree}
BRANCH: {branch}

RELAXED RULES:
✅ If branch data unavailable → USE degree-level data
✅ If specific category unavailable → USE general category
✅ Accept 2023-24 data if newer unavailable

SEARCH HARDER:
- Check placement reports
- Check admission brochures
- Check official PDFs

RETURN ALL 5 FIELDS with valid data.
Same JSON format.
"""
            
            else:  # attempt == 3
                logger.warning(f"🔄 [Attempt {attempt}/{MAX_RETRIES}] Final attempt for {college_name}")
                prompt = f"""
FINAL ATTEMPT: Return BEST available data.

{college_name} - {degree} - {branch}

MAXIMUM FLEXIBILITY:
✅ Overall college data acceptable
✅ Approximate/range values acceptable
✅ Older data (2022-23) acceptable
✅ Any reliable source

TRY YOUR BEST to fill ALL 5 fields.
Same JSON format.
"""
            
            # =============================
            # API CALL WITH TIMEOUT
            # =============================
            try:
                # Rate limit delay
                await asyncio.sleep(base_delay)
                
                # Call Gemini
                loop = asyncio.get_event_loop()
                response = await asyncio.wait_for(
                    loop.run_in_executor(
                        None,
                        partial(model.generate_content, prompt)
                    ),
                    timeout=120.0
                )
                
                text = response.text.strip()
                
                # Clean markdown
                if text.startswith("```"):
                    text = text.replace("```json", "").replace("```", "").strip()
                
                # Parse JSON
                try:
                    extracted = json.loads(text)
                except Exception as e:
                    logger.error(f"   🔴 JSON parse error: {str(e)[:100]}")
                    if attempt < MAX_RETRIES:
                        await asyncio.sleep(base_delay * attempt)
                        continue
                    else:
                        logger.error(f"   ❌ Data not found after {MAX_RETRIES} attempts (JSON parse failed)")
                        return {"error": "invalid_json_after_retries"}
                
                # =============================
                # CHECK COMPLETENESS
                # =============================
                is_complete, missing_fields = CollegeStrictGeminiExtractor._is_data_complete(extracted)
                
                if is_complete:
                    logger.success(f"   ✅ SUCCESS: All fields extracted for {college_name}")
                    return extracted
                else:
                    # Log missing fields
                    logger.warning(f"   ⚠️ INCOMPLETE: Missing fields → {missing_fields}")
                    
                    if attempt < MAX_RETRIES:
                        retry_delay = base_delay * (attempt + 1)
                        logger.info(f"   ⏳ Waiting {retry_delay}s before retry...")
                        await asyncio.sleep(retry_delay)
                        continue
                    else:
                        # Max retries exhausted
                        total_fields = 5
                        found_fields = total_fields - len(missing_fields)
                        logger.warning(f"   ⚠️ INCOMPLETE: Saving {found_fields}/{total_fields} fields (acceptable threshold met)")
                        logger.warning(f"   ❌ Missing fields: {missing_fields}")
                        logger.warning(f"   ❌ Incomplete data will NOT be saved to cache")
                        return {
                            "error": "incomplete_data_after_retries",
                            "missing_fields": missing_fields,
                            "found_fields": found_fields,
                            "total_fields": total_fields
                        }
            
            except asyncio.TimeoutError:
                logger.error(f"   ⏱️ Timeout error (attempt {attempt})")
                if attempt < MAX_RETRIES:
                    continue
                else:
                    logger.error(f"   ❌ Data not found: Timeout after {MAX_RETRIES} attempts")
                    return {"error": "timeout_exceeded"}
            
            except ResourceExhausted:
                logger.warning(f"   🟡 Rate limit hit (attempt {attempt})")
                await asyncio.sleep(60)
                if attempt < MAX_RETRIES:
                    continue
                else:
                    logger.error(f"   ❌ Data not found: Quota exhausted")
                    return {"error": "quota_exhausted"}
            
            except GoogleAPIError as e:
                logger.error(f"   🔴 API Error: {str(e)}")
                return {"error": f"api_error: {str(e)}"}
            
            except Exception as e:
                logger.error(f"   🔴 Unexpected error: {str(e)}")
                return {"error": f"unexpected: {str(e)}"}
        
        # Should not reach here, but safety fallback
        logger.error(f"   ❌ Data not found: All retries exhausted for {college_name}")
        return {"error": "all_retries_failed"}