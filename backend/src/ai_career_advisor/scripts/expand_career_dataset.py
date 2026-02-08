import asyncio
import json
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ai_career_advisor.core.database import get_db, AsyncSessionLocal as async_session_factory
from ai_career_advisor.models.career_attributes import CareerAttributes
from ai_career_advisor.core.model_manager import ModelManager
from ai_career_advisor.core.logger import logger

# Industry categories to expand
INDUSTRIES = [
    "Information Technology & AI",
    "Healthcare & Medicine",
    "Finance & Banking",
    "Creative Arts & Design",
    "Legal & Civil Services",
    "Engineering & Manufacturing",
    "Management & Business",
    "Media & Communications",
    "Education & Research",
    "Hospitality & Tourism"
]

EXPANSION_PROMPT = """
You are a career data expert for the Indian market. Generate 6 distinct and diverse career profiles for the industry: "{industry}".

For each career, provide data in the following JSON format:
{{
  "career_name": "Full Name",
  "career_category": "{industry}",
  "short_description": "2-3 comprehensive sentences",
  "required_skills": ["skill1", "skill2", "skill3", "skill4"],
  "interest_tags": ["tag1", "tag2", "tag3"],
  "personality_fit": ["trait1", "trait2"],
  "min_education": "10th/12th/graduate/postgraduate",
  "preferred_streams": ["science/commerce/arts"],
  "required_degrees": ["Degree 1", "Degree 2"],
  "salary_range": "X-Y LPA",
  "min_salary_lpa": X,
  "max_salary_lpa": Y,
  "work_style": "remote/office/hybrid",
  "difficulty_level": 1-5,
  "growth_potential": "high/medium/low",
  "job_availability": "high/medium/low",
  "top_cities": ["City1", "City2"],
  "popularity_score": 0.5-0.9
}}

Ensure:
1. Degrees are common in India (e.g., B.Tech, MBBS, CA, LLB, MBA).
2. Salary ranges are realistic for Indian market in LPA.
3. Streams match Indian higher secondary system.
4. RETURN ONLY A JSON LIST of 6 objects. No markdown formatting.
"""

async def expand_dataset():
    logger.info("🚀 Starting Advanced Career Data Expansion...")
    
    total_added = 0
    
    async with async_session_factory() as db:
        for industry in INDUSTRIES:
            logger.info(f"📁 Processing industry: {industry}")
            
            prompt = EXPANSION_PROMPT.format(industry=industry)
            
            try:
                # Generate careers using LLM
                response_text = await ModelManager.generate_smart(prompt)
                
                # Clean JSON
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].strip()
                
                careers_data = json.loads(response_text)
                
                if not isinstance(careers_data, list):
                    logger.warning(f"⚠️ Response for {industry} was not a list. Skipping.")
                    continue
                
                for data in careers_data:
                    # Check if exists
                    res = await db.execute(
                        select(CareerAttributes).where(CareerAttributes.career_name == data["career_name"])
                    )
                    if res.scalars().first():
                        logger.info(f"   ⏩ Skipping (already exists): {data['career_name']}")
                        continue
                    
                    logger.info(f"   ✨ Generating semantic vector for: {data['career_name']}")
                    
                    # Create semantic vector based on name + description + skills
                    text_for_embedding = f"{data['career_name']}. {data['short_description']}. Skills: {', '.join(data['required_skills'])}. Interests: {', '.join(data['interest_tags'])}"
                    
                    try:
                        vector = await ModelManager.get_embedding(text_for_embedding)
                        data["semantic_vector"] = vector
                    except Exception as ve:
                        logger.error(f"   ❌ Vector error for {data['career_name']}: {ve}")
                        data["semantic_vector"] = None
                    
                    # Create object
                    career = CareerAttributes(**data)
                    db.add(career)
                    total_added += 1
                
                await db.commit()
                logger.success(f"✅ Added {len(careers_data)} careers for {industry}")
                
            except Exception as e:
                logger.error(f"❌ Error processing {industry}: {e}")
                await db.rollback()
                
    logger.success(f"🎊 Expansion complete! Total added: {total_added} careers.")

if __name__ == "__main__":
    asyncio.run(expand_dataset())
