import json
import google.generativeai as genai
from ai_career_advisor.core.config import settings
from ai_career_advisor.core.logger import logger
import asyncio
from functools import partial
from datetime import datetime

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash-lite")


class EntranceExamLLM:
    
    @staticmethod
    async def get_entrance_exam_info(
        *,
        college_name: str,
        degree: str,
        branch: str = None
    ) -> dict:
        
        logger.info(f"Fetching entrance exam for {college_name} - {degree} {branch or ''}")
        
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        if current_month >= 6:
            academic_year = current_year + 1
        else:
            academic_year = current_year
        
        prompt = f"""
You are an Indian education entrance exam expert.

COLLEGE: {college_name}
DEGREE: {degree}
BRANCH: {branch or 'General'}
ACADEMIC YEAR: {academic_year}

Task: Identify the ACTIVE entrance exam required for admission.

Return ONLY valid JSON (no markdown):

{{
  "exam_name": "JEE Main",
  "exam_full_name": "Joint Entrance Examination - Main",
  "conducting_body": "NTA",
  "exam_date": "2026-04-06",
  "registration_start_date": "2026-02-01",
  "registration_end_date": "2026-03-15",
  "exam_pattern": "MCQ",
  "official_website": "https://jeemain.nta.nic.in",
  "syllabus_link": "https://jeemain.nta.nic.in/syllabus",
  "academic_year": "{academic_year}",
  "is_active": true,
  "status": "upcoming"
}}

Rules:
- Return ONLY active/upcoming exams (not past exams)
- Use actual {academic_year} dates
- If registration closed, set status to "exam_pending"
- If exam finished, set is_active to false
- Be accurate with Indian exam calendars

Examples:
- IIT Bombay, BTech, CS → JEE Advanced
- AIIMS Delhi, MBBS → NEET UG
- Delhi University, BSc, CS → CUET UG
- BITS Pilani, BTech → BITSAT
- IIM Ahmedabad, MBA → CAT
- NLU Delhi, LLB → CLAT
"""
        
        try:
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(None, partial(model.generate_content, prompt)),
                timeout=60.0
            )
            
            text = response.text.strip()
            
            if text.startswith("```"):
                text = text.replace("```json", "").replace("```", "").strip()
            
            exam_data = json.loads(text)
            
            logger.success(f"Found exam: {exam_data.get('exam_name')}")
            return exam_data
        
        except asyncio.TimeoutError:
            logger.error("Timeout fetching exam data")
            return {"error": "timeout"}
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {str(e)}")
            return {"error": "invalid_json"}
        
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return {"error": str(e)}
