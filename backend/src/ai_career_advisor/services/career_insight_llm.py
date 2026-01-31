import json
import asyncio
from ai_career_advisor.core.logger import logger
from ai_career_advisor.core.model_manager import ModelManager  


def _normalize_projects(projects):
    """
    Always return projects as:
    {
        "production": List[str],
        "research": List[str]
    }
    """
    if isinstance(projects, dict):
        return {
            "production": projects.get("production", []),
            "research": projects.get("research", [])
        }

    if isinstance(projects, list):
        return {
            "production": projects[:2],
            "research": projects[2:3] if len(projects) > 2 else []
        }

    return {
        "production": [],
        "research": []
    }


def generate_career_insight_sync(career_name: str) -> dict:
    """Synchronous wrapper for generate_career_insight"""
    return asyncio.run(generate_career_insight(career_name))


async def generate_career_insight(career_name: str) -> dict:
    logger.info(f"🎯 Generating Top 1% insight for: {career_name}")

    prompt = f"""
You are a Career Excellence Generator. Generate career preparation insights for "{career_name}".

Return ONLY valid JSON with these exact keys:
{{
  "skills": ["skill1", "skill2", "skill3", "skill4", "skill5", "skill6", "skill7", "skill8"],
  "internships": ["company1", "company2", "company3"],
  "projects": {{
    "production": ["project1", "project2"],
    "research": ["research_project1"]
  }},
  "programs": ["program1", "program2"],
  "top_salary": "₹XX-XX LPA in India / $XXX-XXX in USA"
}}

For top_salary field:
- Provide realistic top 1% salary range in India (in LPA format)
- Also include international range if applicable
- Example: "₹50-80 LPA in India / $150k-250k in USA"

Rules:
- Return ONLY the JSON object
- No markdown formatting
- No explanation text
- No ```json``` tags
- Just pure JSON
"""

    try:
        logger.info("📤 Using ModelManager with smart fallback...")
        raw_text = await ModelManager.generate_smart(prompt)
        
        logger.info(f"📦 Raw LLM Response: {raw_text[:200]}...")

        
        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json", "").replace("```", "").strip()
        elif raw_text.startswith("```"):
            raw_text = raw_text.replace("```", "").strip()

        
        data = json.loads(raw_text)

        
        required_keys = ["skills", "internships", "projects", "programs", "top_salary"]
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required key: {key}")

        
        data["projects"] = _normalize_projects(data.get("projects"))

        logger.success(f"✅ Career insight generated for {career_name}")
        return data

    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON parsing failed for {career_name}: {e}")
        logger.error(f"Raw response was: {raw_text if 'raw_text' in locals() else 'No response'}")
        raise
    except Exception as e:
        logger.error(f"❌ LLM failed for {career_name}: {e}")
        raise
