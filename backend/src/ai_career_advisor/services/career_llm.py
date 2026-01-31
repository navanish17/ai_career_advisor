import json
import asyncio
from ai_career_advisor.core.logger import logger
from ai_career_advisor.core.model_manager import ModelManager


def generate_career_details_sync(career_name: str) -> dict:
    """
    Generates career description, market trend and salary range
    using Gemini LLM in a STRICT JSON format (synchronous wrapper).
    """
    return asyncio.run(generate_career_details(career_name))


async def generate_career_details(career_name: str) -> dict:
    """
    Generates career description, market trend and salary range
    using Gemini LLM in a STRICT JSON format (async version).
    """

    logger.info(f"📚 Generating career data for: {career_name}")

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
        # Use ModelManager with smart fallback
        raw_text = await ModelManager.generate_smart(prompt)
        data = json.loads(raw_text)

        logger.success(f"✅ Career data generated: {career_name}")
        return data

    except Exception as e:
        logger.error(f"❌ Failed to generate career data for {career_name}: {str(e)}")
        raise

