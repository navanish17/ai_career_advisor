import pandas as pd
import asyncio

from ai_career_advisor.core.database import AsyncSessionLocal
from ai_career_advisor.models.college import College
from ai_career_advisor.core.logger import logger


CSV_PATH = r"D:\Cdac_project\project_02\nirf_ranking.csv"


async def seed_colleges():
    logger.info("Starting NIRF colleges seeding")

    df = pd.read_csv(CSV_PATH)

    async with AsyncSessionLocal() as session:
        for _, row in df.iterrows():
            college = College(
                name=row["Name"].strip(),
                city=row["City"].strip(),
                state=row["State"].strip(),
                nirf_rank=int(row["Rank"]) if not pd.isna(row["Rank"]) else None,
                website=row.get("Website")
            )
            session.add(college)

        await session.commit()

    logger.info("✅ NIRF colleges seeded successfully")


if __name__ == "__main__":
    asyncio.run(seed_colleges())
