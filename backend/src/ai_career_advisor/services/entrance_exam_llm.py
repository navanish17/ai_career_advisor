import json
from ai_career_advisor.core.config import settings
from ai_career_advisor.core.logger import logger
import httpx
from datetime import datetime


class EntranceExamLLM:
    
    @staticmethod
    async def get_entrance_exam_info(
        *,
        college_name: str,
        degree: str,
        branch: str = None
    ) -> dict:
        
        logger.info(f"Fetching entrance exam for {college_name} - {degree} {branch or ''} using Perplexity")
        
        PERPLEXITY_API_KEY = settings.PERPLEXITY_API_KEY or ""
        PERPLEXITY_MODEL = "sonar-pro"

        if not PERPLEXITY_API_KEY:
            logger.error("❌ Perplexity API key missing")
            return {"error": "api_key_missing"}

        current_year = datetime.now().year
        current_month = datetime.now().month
        
        if current_month >= 6:
            academic_year = current_year + 1
        else:
            academic_year = current_year
        
        prompt = f"""
You are an expert Indian education counselor. Find strict entrance exam details.

TARGET:
College: {college_name}
Degree: {degree}
Branch: {branch or 'General'}
Target Academic Year: {academic_year}

TASK:
Identify the OFFICIAL entrance exam required for admission.

SEARCH STRATEGY:
1. Check official admission page of {college_name}
2. Check exams like JEE Main, JEE Advanced, NEET, CAT, GATE, CUET (if applicable)
3. Check state-level CETs (e.g., MHT CET, KCET, WBJEE)

OUTPUT JSON FORMAT:
{{
  "exam_name": "Exam Name",
  "exam_full_name": "Full Name",
  "conducting_body": "Authority Name",
  "exam_date": "YYYY-MM-DD",
  "registration_start_date": "YYYY-MM-DD",
  "registration_end_date": "YYYY-MM-DD",
  "exam_pattern": "CBT/Offline",
  "official_website": "URL",
  "syllabus_link": "URL",
  "academic_year": "{academic_year}",
  "is_active": true/false,
  "status": "upcoming/ongoing/completed"
}}

RULES:
✅ Return ONLY valid JSON
✅ Use actual/tentative dates for {academic_year}
✅ If dates announced: use exact date
✅ If dates NOT announced: estimate based on previous year trends and label "Tentative" in status
✅ If exam is over for this cycle, set is_active: false
"""
        
        try:
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
                    logger.error(f"❌ Perplexity API error: {response.status_code}")
                    return {"error": f"api_error_{response.status_code}"}
                
                data = response.json()
                text = data["choices"][0]["message"]["content"].strip()
                
                # Clean markdown
                if text.startswith("```"):
                    text = text.replace("```json", "").replace("```", "").strip()
                
                exam_data = json.loads(text)
                logger.success(f"Found exam: {exam_data.get('exam_name')}")
                return exam_data
        
        except Exception as e:
            logger.error(f"Error fetching exam data: {e}")
            return {"error": str(e)}
