import json
import requests
from ai_career_advisor.core.logger import logger
from ai_career_advisor.core.config import settings
from ai_career_advisor.services.llm_provider import get_llm_provider

import google.generativeai as genai

genai.configure(api_key=settings.GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.5-flash-lite")


def _normalize_projects(projects):
    """
    Always return projects as:
    {
        "production": List[str],
        "research": List[str]
    }
    """

    # Case 1: Already correct
    if isinstance(projects, dict):
        return {
            "production": projects.get("production", []),
            "research": projects.get("research", [])
        }

    # Case 2: Old / bad format (list)
    if isinstance(projects, list):
        return {
            "production": projects[:2],
            "research": projects[2:3] if len(projects) > 2 else []
        }

    # Case 3: Anything unexpected
    return {
        "production": [],
        "research": []
    }


def generate_career_insight(career_name: str) -> dict:
    logger.info(f"Generating Top 1% insight for: {career_name}")

    prompt = f"""
You are a Career Excellence Generator who give data to become 1% in selected career field.

Generate career preparation insights for "{career_name}".

Return STRICT JSON with ONLY these keys:
- skills (8 items)
- internships (2–3 well-known companies or programs)
- projects:
  - production (2 real-world production grade projects)
  - research (1 research-oriented project)
- programs (1–2 popular credibility programs if applicable like Gsoc, mlh fellowship)

Rules:
- No explanations
- No bullets
- No markdown
- JSON only
"""

    provider = get_llm_provider()

    try:
        if provider == "perplexity":
            logger.info("Using Perplexity LLM")

            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.PERPLEXITY_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "sonar",
                    "messages": [
                        {"role": "system", "content": "Return JSON only"},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.2,
                },
                timeout=35,
            )

            raw_text = response.json()["choices"][0]["message"]["content"]

        else:
            logger.info("Using Gemini LLM")
            response = gemini_model.generate_content(prompt)
            raw_text = response.text.strip()

        data = json.loads(raw_text)

        # ✅ CRITICAL FIX
        data["projects"] = _normalize_projects(data.get("projects"))

        logger.success(f"Career insight generated for {career_name}")
        return data

    except Exception as e:
        logger.error(f"LLM failed for {career_name}: {e}")
        raise
