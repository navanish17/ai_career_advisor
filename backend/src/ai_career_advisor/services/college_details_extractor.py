import json
import asyncio
from functools import partial
from ai_career_advisor.core.logger import logger
from ai_career_advisor.core.config import settings
from ai_career_advisor.core.model_manager import ModelManager


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
            
            field_data = extracted[field]
            
            # Handle both nested dict and flat string
            if isinstance(field_data, dict):
                value = field_data.get("value", "")
            else:
                value = str(field_data)
            
            # Check if value is null, empty, or "Not available"
            if (not value or 
                not str(value).strip() or 
                str(value).strip().lower() in ["null", "none", "n/a"]):
                missing.append(field)
            # Allow "Not available" as a valid value
            # Don't mark "Not available" as missing
        
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
        
        # Perplexity configuration
        PERPLEXITY_API_KEY = settings.PERPLEXITY_API_KEY or ""
        PERPLEXITY_MODEL = "sonar-pro"


        if not PERPLEXITY_API_KEY:
            logger.error("❌ Perplexity API key missing")
            return {"error": "api_key_missing"}


        # =============================
        # SINGLE STRICT PROMPT
        # =============================
        prompt = f"""You are a precise college data extraction assistant with web search access.


TARGET PROGRAM:
College: {college_name}
Degree: {degree}
Branch: {branch}


DATA REQUIRED (for {degree} in {branch} ONLY):
1. Official college website URL
2. Annual tuition fees (academic year, NOT hostel/mess)
3. Average placement package
4. Highest placement package  
5. Entrance exam name
6. Cutoff (rank/percentile/score)


SEARCH STRATEGY:
Priority 1: Official {college_name} website (look for: admissions page, fee structure PDFs, placement reports)
Priority 2: AICTE/NIRF official data
Priority 3: Verified portals (Shiksha.com, Careers360.com, CollegeDunia.com)


STRICT RULES:
✅ ONLY extract data for {degree} in {branch} - ignore other branches/degrees
✅ Prefer 2025-26 data, accept 2024-25 if unavailable
✅ Include data source URL for each field
✅ If data not found after thorough search → mark "Not available"
✅ For cutoffs: specify year, category (General/OBC/SC/ST), and exam type
✅ For fees: annual tuition only (exclude hostel/other charges)
✅ For college website: provide official .edu.in or .ac.in domain (NOT third-party portals)


OUTPUT FORMAT (valid JSON only):
{{
  "college_name": "{college_name}",
  "degree": "{degree}",
  "branch": "{branch}",
  "data_year": "2025-26 or 2024-25 or year found",
  
  "college_website": {{
    "value": "https://official-college-website.ac.in",
    "note": "Official college domain"
  }},
  
  "fees": {{
    "value": "₹X per year",
    "source_url": "URL",
    "note": "any clarification if needed"
  }},
  
  "avg_package": {{
    "value": "X LPA",
    "source_url": "URL",
    "note": "clarification"
  }},
  
  "highest_package": {{
    "value": "X LPA",
    "source_url": "URL",
    "note": "clarification"
  }},
  
  "entrance_exam": {{
    "value": "Exam name",
    "source_url": "URL",
    "note": "clarification"
  }},
  
  "cutoff": {{
    "value": "Rank/Percentile (year, category)",
    "source_url": "URL",
    "note": "clarification"
  }}
}}


IMPORTANT: Return ONLY the JSON object, no additional text.
"""
        logger.info(f"📊 Extracting details for {college_name} using Perplexity Sonar Pro")


        try:
            import httpx


            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers={
                        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": PERPLEXITY_MODEL,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a precise data extraction assistant. Return ONLY valid JSON."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"❌ Perplexity API error: {response.status_code} - {response.text}")
                    return {"error": f"perplexity_api_error_{response.status_code}"}


                data = response.json()
                text = data["choices"][0]["message"]["content"].strip()
                
                # Clean markdown
                if text.startswith("```"):
                    text = text.replace("```json", "").replace("```", "").strip()


                try:
                    extracted = json.loads(text)
                except json.JSONDecodeError:
                    logger.error(f"❌ JSON parse failed for {college_name}")
                    return {"error": "invalid_json_after_retries", "partial_data": {}}


                # Validate completeness
                is_complete, missing = CollegeStrictGeminiExtractor._is_data_complete(extracted)
                
                # Always return data, even if incomplete
                if not is_complete:
                    logger.warning(f"⚠️ Missing fields: {missing}")
                    return {
                        "warning": "incomplete_data",
                        "missing_fields": missing, 
                        "partial_data": extracted
                    }


                logger.success(f"✅ Success: Extracted all details for {college_name}")
                return extracted


        except Exception as e:
            logger.error(f"❌ Extraction error: {e}")
            return {"error": str(e)}
