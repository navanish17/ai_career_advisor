import json
import time
from ai_career_advisor.core.logger import logger
from ai_career_advisor.core.config import settings

import google.generativeai as genai


# Gemini configuration
genai.configure(api_key=settings.GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash-lite")


def generate_career_details(career_name: str) -> dict:
    """
    Generates career description, market trend and salary range
    using Gemini LLM in a STRICT JSON format.
    """

    logger.info(f"Generating LLM data for career: {career_name}")

    prompt = f"""
You are a Career Summary Generator.

Generate details for the career "{career_name}".  

Return STRICT JSON with ONLY these keys:

- description (1 line, simple academic tone)
- market_trend (1 short line)
- salary_range (for india in Ruppes currency, salary should be in the form of like 3lpa to 7lpa )

Rules:
- No skills
- No career advice
- No bullets
- No extra text
- No markdown
- JSON only
"""

    try:
        response = model.generate_content(prompt)

        # Gemini returns text, parse it safely
        raw_text = response.text.strip()
        data = json.loads(raw_text)

        logger.success(f"LLM data generated for career: {career_name}")
        return data

    except Exception as e:
        logger.error(f"Failed to generate career data for {career_name}: {e}")
        raise
