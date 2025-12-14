import asyncio
from sqlalchemy import select

from ai_career_advisor.core.logger import logger
from ai_career_advisor.core.database import AsyncSessionLocal
from ai_career_advisor.models.degree import Degree
from ai_career_advisor.services.degree_llm import generate_degree_description


async def generate_and_save_descriptions():
    async with AsyncSessionLocal() as session:

        # 1️⃣ Fetch only degrees with NULL description
        result = await session.execute(
            select(Degree).where(Degree.short_description.is_(None))
        )
        degrees = result.scalars().all()

        if not degrees:
            logger.info("All degrees already have descriptions.")

            return

        logger.info(f"Found {len(degrees)} degrees without description")


        for degree in degrees:
            try:
                logger.info(f"Generating description for degree: {degree.name}")


                description = generate_degree_description(degree.name)

                # 2️⃣ Save to DB
                degree.short_description = description
                session.add(degree)

                # Rate-limit safety (Gemini free tier)
                await asyncio.sleep(7)

            except Exception as e:
                # ❌ Fail-safe: skip & continue
                logger.error(f"Failed to generate description for {degree.name}: {e}")

                continue

        # 3️⃣ Commit once (safe + efficient)
        await session.commit()

    logger.success("Degree descriptions generated and saved successfully!")



if __name__ == "__main__":
    asyncio.run(generate_and_save_descriptions())
