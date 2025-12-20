import json
from ai_career_advisor.core.logger import logger
from ai_career_advisor.core.config import settings
import google.generativeai as genai

genai.configure(api_key=settings.GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash-lite")


def generate_career_insight(career_name: str) -> dict:
    logger.info(f"Generating career insight for: {career_name}")

    prompt = f"""
You are a Career Excellence Generator who give advise to become 1% in selected career field.

Generate career preparation insights for "{career_name}".

Return STRICT JSON with ONLY these keys:
- top skills (8 items)
- internships (2–3 well-known companies or programs)
- projects:
  - production (2 real-world production grade projects)
  - research (1 research-oriented project)
- programs (1–2 popular credibility programs if applicable like Gsoc, mlh fellowship for all CS Students)

Rules:
- No explanations
- No bullets
- No extra text
- No markdown
- JSON only
"""

    try:
        response = model.generate_content(prompt)
        data = json.loads(response.text.strip())

        logger.success(f"Career insight generated for: {career_name}")
        return data

    except Exception as e:
        logger.error(f"Career insight generation failed for {career_name}: {e}")
        raise
