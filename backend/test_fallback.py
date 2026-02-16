import asyncio
import os
from ai_career_advisor.services.career_normalizer import CareerNormalizerService
from ai_career_advisor.core.logger import logger

# Force configure logging
import logging
logging.basicConfig(level=logging.INFO)

async def test_fallback():
    print("🚀 Testing Career Normalizer Fallback...")
    
    # This should fail on Gemini (expired key) and succeed on Sonar
    result = await CareerNormalizerService.normalize_and_validate("software engineer")
    
    print("\n📝 Result:")
    print(result)

if __name__ == "__main__":
    asyncio.run(test_fallback())
