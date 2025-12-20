import asyncio
import time
from sqlalchemy import select

from ai_career_advisor.core.database import AsyncSessionLocal
from ai_career_advisor.models.career import Career
from ai_career_advisor.services.career_llm import generate_career_details
from ai_career_advisor.core.logger import logger


DELAY_SECONDS = 8          # safe for Gemini free tier
MAX_RETRY = 2              # per career


async def seed_career_llm():
    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(Career).where(Career.description.is_(None))
        )
        careers = result.scalars().all()

        if not careers:
            logger.success("✅ All careers already have LLM data.")
            return

        logger.info(f"🔍 Found {len(careers)} careers without description")

        for career in careers:
            attempts = 0

            while attempts < MAX_RETRY:
                try:
                    logger.info(f"⚙️ Generating LLM data for: {career.name}")

                    data = generate_career_details(career.name)

                    career.description = data.get("description")
                    career.market_trend = data.get("market_trend")
                    career.salary_range = data.get("salary_range")

                    session.add(career)
                    await session.commit()

                    logger.success(f"✅ Updated career: {career.name}")
                    break

                except Exception as e:
                    attempts += 1
                    logger.error(
                        f"❌ Attempt {attempts} failed for {career.name}: {e}"
                    )

                    if attempts >= MAX_RETRY:
                        logger.warning(
                            f"⏭️ Skipping career after retries: {career.name}"
                        )
                    else:
                        time.sleep(10)

            time.sleep(DELAY_SECONDS)

    logger.success("🎉 Career LLM seeding completed!")


if __name__ == "__main__":
    asyncio.run(seed_career_llm())
