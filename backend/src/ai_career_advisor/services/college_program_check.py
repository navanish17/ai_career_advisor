from ai_career_advisor.core.config import settings
from ai_career_advisor.core.logger import logger
import asyncio
from functools import partial
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ai_career_advisor.models.college_program_cache import CollegeProgramCache
import httpx
import os


class CollegeProgramCheckService:
    """
    Service to check if a college offers a specific program
    Features:
    - Database caching to avoid repeated LLM calls
    - Perplexity Sonar Pro only (Gemini removed)
    """
    
    # Perplexity configuration
    PERPLEXITY_API_KEY = settings.PERPLEXITY_API_KEY or ""
    PERPLEXITY_MODEL = "sonar-pro"
    
    @classmethod
    async def check_with_cache(
        cls,
        db: AsyncSession,
        college_id: int,
        college_name: str,
        degree: str,
        branch: str
    ) -> bool:
        """
        Check if college offers program, using cache first
        """
        # Check cache first
        result = await db.execute(
            select(CollegeProgramCache).where(
                CollegeProgramCache.college_id == college_id,
                CollegeProgramCache.degree == degree,
                CollegeProgramCache.branch == branch
            )
        )
        cached = result.scalars().first()
        
        if cached:
            logger.debug(f"💾 Cache hit: {college_name} - {degree} {branch} = {cached.offers_program}")
            return cached.offers_program
        
        # Not in cache, check using LLM
        logger.debug(f"🔍 Cache miss: Checking {college_name} - {degree} {branch}")
        offers_program = await cls.check(
            college_name=college_name,
            degree=degree,
            branch=branch
        )
        
        # Save to cache (will be committed at endpoint level)
        cache_entry = CollegeProgramCache(
            college_id=college_id,
            degree=degree,
            branch=branch,
            offers_program=offers_program
        )
        db.add(cache_entry)
        
        logger.success(f"💾 Cached result: {college_name} - {offers_program}")
        return offers_program
    
    @classmethod
    async def check(cls, *, college_name: str, degree: str, branch: str) -> bool:
        """
        Fast yes/no check using Perplexity Sonar Pro
        """
        prompt = f"""Verify if {college_name} offers EXACTLY "{degree}" in "{branch}".

SEARCH:
- Official {college_name} website
- Current course catalog/admissions page
- AICTE/UGC/JoSAA databases (if applicable)

STRICT MATCHING RULES:
❌ BSc ≠ MSc ≠ BTech ≠ BE (degree level must match exactly)
❌ "BSc Physics" ≠ "BTech Engineering Physics" (different degrees)
❌ Physics department existing ≠ offering "{degree} in {branch}"
✅ Allow minor naming: "Computer Science" = "CS" = "CSE" (same degree only)

Return ONLY one word:
- true: EXACT program "{degree} in {branch}" exists with verified evidence
- false: Program doesn't exist, different degree level found, or unsure

Answer:"""
        
        # Try Perplexity Sonar Pro
        result = await cls._try_perplexity(prompt, college_name, degree, branch)
        if result is not None:
            return result
        
        # Failed
        logger.error(f"❌ Check failed for {college_name}")
        return False
    
    @classmethod
    async def _try_perplexity(cls, prompt: str, college_name: str, degree: str, branch: str) -> bool | None:
        """Try Perplexity Sonar Pro as fallback"""
        if not cls.PERPLEXITY_API_KEY:
            logger.warning("⚠️ Perplexity API key not configured")
            return None
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers={
                        "Authorization": f"Bearer {cls.PERPLEXITY_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": cls.PERPLEXITY_MODEL,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a helpful assistant. Answer only with 'true' or 'false'."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data["choices"][0]["message"]["content"].strip().lower()
                    result = "true" in answer
                    logger.debug(f"✅ Perplexity Sonar Pro: {result}")
                    return result
                else:
                    logger.error(f"❌ Perplexity API error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Perplexity error: {e}")
            return None
