import asyncio
import time
from sqlalchemy import select

from ai_career_advisor.core.database import AsyncSessionLocal
from ai_career_advisor.core.logger import logger
from ai_career_advisor.models.career import Career
from ai_career_advisor.models.career_insight import CareerInsight
from ai_career_advisor.services.career_insight_llm import generate_career_insight


DELAY_SECONDS = 15      
MAX_RETRIES = 2


async def seed_career_insights():
    
    async with AsyncSessionLocal() as session:

        # Fetch all careers
        result = await session.execute(select(Career))
        careers = result.scalars().all()

        logger.info(f"Found {len(careers)} careers")


        for career in careers:

            # Skip if insight already exists
            exists = await session.execute(
                select(CareerInsight)
                .where(CareerInsight.career_id == career.id)
            )
            if exists.scalar_one_or_none():
                logger.info(f"Skipping existing insight: {career.name}")
                continue

            logger.info(f"Generating Top 1% insight for: {career.name}")

            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    data = generate_career_insight(career.name)

                    insight = CareerInsight(
                        career_id=career.id,
                        skills=data["skills"],
                        internships=data["internships"],
                        projects=data["projects"],
                        programs=data["programs"],
                    )

                    session.add(insight)
                    await session.commit()

                    logger.success(f"✅ Insight saved for {career.name}")
                    break

                except Exception as e:
                    logger.error(
                        f"Attempt {attempt} failed for {career.name}: {e}"
                    )

                    if attempt == MAX_RETRIES:
                        logger.warning(
                            f"Skipping career after retries: {career.name}"
                        )

                time.sleep(DELAY_SECONDS)

    logger.success("Career Insight seeding completed!")


if __name__ == "__main__":
    asyncio.run(seed_career_insights())
