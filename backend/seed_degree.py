import asyncio
import sys
import os

# Add backend to path
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BACKEND_DIR)

from sqlalchemy import select
from ai_career_advisor.core.logger import logger
from ai_career_advisor.core.database import AsyncSessionLocal
from ai_career_advisor.models.degree import Degree


DEGREES = [
    ("BE / BTech", "science", "12th Science (PCM)", 4, "Bachelor of Engineering/Technology - Professional degree in engineering with specializations like Computer Science, Mechanical, Civil, Electrical, and more."),
    ("BSc", "science", "12th Science", 3, "Bachelor of Science - Academic degree covering subjects like Physics, Chemistry, Mathematics, Biology, Computer Science, and other scientific disciplines."),
    ("BCA", "science", "12th (Any stream, Maths preferred)", 3, "Bachelor of Computer Applications - Focused on computer programming, software development, and IT fundamentals."),
    ("MBBS", "science", "12th Science (PCB + NEET)", 5.5, "Bachelor of Medicine and Bachelor of Surgery - Professional medical degree to become a doctor. Requires NEET qualification."),
    ("BDS", "science", "12th Science (PCB + NEET)", 5, "Bachelor of Dental Surgery - Professional degree in dentistry. Requires NEET qualification."),
    ("BAMS", "science", "12th Science (PCB + NEET)", 5.5, "Bachelor of Ayurvedic Medicine and Surgery - Traditional Indian medicine system. Requires NEET qualification."),
    ("BHMS", "science", "12th Science (PCB)", 5.5, "Bachelor of Homeopathic Medicine and Surgery - Alternative medicine system focusing on homeopathy."),
    ("BSc Nursing", "science", "12th Science (PCB)", 4, "Bachelor of Science in Nursing - Professional nursing degree for healthcare and patient care."),
    ("BPT", "science", "12th Science (PCB)", 4.5, "Bachelor of Physiotherapy - Degree in physical therapy and rehabilitation sciences."),
    ("BPharm", "science", "12th Science (PCB/PCM)", 4, "Bachelor of Pharmacy - Pharmaceutical sciences degree covering drug composition, manufacturing, and dispensing."),
    ("BArch", "science", "12th Science (PCM + NATA)", 5, "Bachelor of Architecture - Professional degree in building design and architecture. Requires NATA exam."),

    ("BCom", "commerce", "12th Commerce", 3, "Bachelor of Commerce - Degree in accounting, finance, taxation, business law, and economics."),
    ("BBA", "commerce", "12th Any Stream", 3, "Bachelor of Business Administration - Management degree covering marketing, HR, finance, and business operations."),
    ("BMS", "commerce", "12th Any Stream", 3, "Bachelor of Management Studies - Similar to BBA with focus on management principles and business strategy."),
    ("BAF", "commerce", "12th Commerce", 3, "Bachelor of Accounting and Finance - Specialized degree in financial accounting, auditing, and taxation."),
    ("BFM", "commerce", "12th Commerce", 3, "Bachelor of Financial Markets - Degree focused on stock markets, investment banking, and financial analysis."),
    ("BBI", "commerce", "12th Commerce", 3, "Bachelor of Banking and Insurance - Specialized degree in banking operations, insurance, and financial services."),

    ("BA", "arts", "12th Any Stream", 3, "Bachelor of Arts - Liberal arts degree with subjects like History, Political Science, Psychology, Sociology, English, and more."),
    ("BFA", "arts", "12th Any Stream", 4, "Bachelor of Fine Arts - Degree in visual arts, painting, sculpture, applied arts, and creative expression."),
    ("BSW", "arts", "12th Any Stream", 3, "Bachelor of Social Work - Degree in social welfare, community development, and social justice."),
    ("LLB", "arts", "Graduation Required", 3, "Bachelor of Laws - Professional law degree. Requires graduation in any stream (3-year LLB)."),
    ("BDes", "arts", "12th Any Stream", 4, "Bachelor of Design - Degree in product design, fashion design, graphic design, and UX/UI design."),
    ("BJMC / BJ / BMM", "arts", "12th Any Stream", 3, "Bachelor of Journalism and Mass Communication - Degree in media, journalism, advertising, and public relations."),
    ("BHM / BSc Hospitality", "arts", "12th Any Stream", 3, "Bachelor of Hotel Management - Degree in hospitality, hotel operations, tourism, and event management."),
]


async def seed_degrees():
    async with AsyncSessionLocal() as session:
        for name, stream, eligibility, duration, description in DEGREES:

            result = await session.execute(
                select(Degree).where(Degree.name == name)
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                # Update description if it's missing
                if not existing.short_description:
                    existing.short_description = description
                    logger.info(f"📝 Updated description for: {name}")
                else:
                    logger.info(f"⏭️ Skipping existing degree: {name}")
                continue

            degree = Degree(
                name=name,
                stream=stream,
                eligibility=eligibility,
                duration_years=duration,
                short_description=description,
                is_active=True
            )

            session.add(degree)
            logger.info(f"✅ Added degree: {name}")

        await session.commit()

    logger.info("Degree seeding completed safely")

if __name__ == "__main__":
    asyncio.run(seed_degrees())
    logger.info("Degree Seeder finished running.")