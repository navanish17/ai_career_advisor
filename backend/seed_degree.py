import asyncio
from sqlalchemy import select
from src.ai_career_advisor.core.logger import logger

from src.ai_career_advisor.core.database import AsyncSessionLocal
from src.ai_career_advisor.models.degree import Degree


DEGREES = [
    ("BE / BTech", "science", "12th Science (PCM)", 4),
    ("BSc", "science", "12th Science", 3),
    ("BCA", "science", "12th (Any stream, Maths preferred)", 3),
    ("MBBS", "science", "12th Science (PCB + NEET)", 5.5),
    ("BDS", "science", "12th Science (PCB + NEET)", 5),
    ("BAMS", "science", "12th Science (PCB + NEET)", 5.5),
    ("BHMS", "science", "12th Science (PCB)", 5.5),
    ("BSc Nursing", "science", "12th Science (PCB)", 4),
    ("BPT", "science", "12th Science (PCB)", 4.5),
    ("BPharm", "science", "12th Science (PCB/PCM)", 4),
    ("BArch", "science", "12th Science (PCM + NATA)", 5),

    ("BCom", "commerce", "12th Commerce", 3),
    ("BBA", "commerce", "12th Any Stream", 3),
    ("BMS", "commerce", "12th Any Stream", 3),
    ("BAF", "commerce", "12th Commerce", 3),
    ("BFM", "commerce", "12th Commerce", 3),
    ("BBI", "commerce", "12th Commerce", 3),

    ("BA", "arts", "12th Any Stream", 3),
    ("BFA", "arts", "12th Any Stream", 4),
    ("BSW", "arts", "12th Any Stream", 3),
    ("LLB", "arts", "Graduation Required", 3),
    ("BDes", "arts", "12th Any Stream", 4),
    ("BJMC / BJ / BMM", "arts", "12th Any Stream", 3),
    ("BHM / BSc Hospitality", "arts", "12th Any Stream", 3),
]


async def seed_degrees():
    async with AsyncSessionLocal() as session:
        for name, stream, eligibility, duration in DEGREES:

            result = await session.execute(
                select(Degree).where(Degree.name == name)
            )
            if result.scalar_one_or_none():
                print(f"⏭️ Skipping existing degree: {name}")
                continue

            degree = Degree(
                name=name,
                stream=stream,
                eligibility=eligibility,
                duration_years=duration,
                is_active=True
            )

            session.add(degree)

        await session.commit()

    print("✅ Degree seeding completed safely")

if __name__ == "__main__":
    asyncio.run(seed_degrees())
    logger.info("Degree Seeder finished running.")