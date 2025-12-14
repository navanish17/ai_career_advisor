import asyncio
from sqlalchemy import select

from ai_career_advisor.core.database import AsyncSessionLocal
from ai_career_advisor.models.degree import Degree
from ai_career_advisor.models.branch import Branch
from ai_career_advisor.core.logger import logger

BRANCHES = {
    "BE / BTech": [
        "Computer / Software",
        "Mechanical / Manufacturing",
        "Civil / Infrastructure",
        "Electrical / Electronics",
        "Chemical / Process"
    ],
    "BSc": ["Physics", "Chemistry", "Mathematics", "Biology"],
    "BCA": ["Software Development", "Data & Analytics", "Cybersecurity"],
    "MBBS": ["Clinical Medicine", "Surgery", "Diagnostics & Public Health"],
    "BDS": ["Dental Practice", "Oral Surgery", "Dental Research"],
    "BAMS": ["Ayurveda Practice", "Panchakarma & Therapy", "Research & Pharmacology"],
    "BHMS": ["Homeopathic Practice", "Clinical Research", "Preventive Healthcare"],
    "BSc Nursing": ["Clinical Nursing", "Community Health", "Nursing Administration"],
    "BPT": ["Orthopedic Physiotherapy", "Sports Physiotherapy", "Neuro Rehabilitation"],
    "BPharm": ["Pharmaceutical Sciences", "Clinical Pharmacy", "Drug Research & Manufacturing"],
    "BArch": ["Architectural Design", "Urban Planning", "Construction Technology"],

    "BCom": ["Accounting", "Finance", "Banking & Insurance"],
    "BBA": ["Management", "Marketing", "Finance", "Human Resources"],
    "BMS": ["Business Management", "Operations", "Strategy"],
    "BAF": ["Accounting", "Financial Analysis", "Auditing"],
    "BFM": ["Financial Markets", "Investment", "Risk Management"],
    "BBI": ["Banking Operations", "Insurance Management", "Financial Services"],

    "BA": ["Humanities", "Social Sciences", "Languages"],
    "BFA": ["Fine Arts", "Visual Design", "Performing Arts"],
    "BSW": ["Social Work Practice", "Community Development", "Welfare Administration"],
    "LLB": ["Legal Practice", "Corporate Law", "Criminal & Civil Law"],
    "BDes": ["Product Design", "UX & Communication Design", "Fashion & Interior Design"],
    "BJMC / BJ / BMM": ["Journalism", "Media Production", "Advertising & Communication"],
    "BHM / BSc Hospitality": ["Hotel Operations", "Tourism & Travel", "Hospitality Management"]
}

async def seed_branches():
    async with AsyncSessionLocal() as session:
        for degree_name, branch_list in BRANCHES.items():

            result = await session.execute(
                select(Degree).where(Degree.name == degree_name)
            )
            degree = result.scalar_one_or_none()

            if not degree:
                logger.warning(f"Degree not found: {degree_name}")
                continue

            for branch_name in branch_list:
                exists = await session.execute(
                    select(Branch).where(
                        Branch.name == branch_name,
                        Branch.degree_id == degree.id
                    )
                )
                if exists.scalar_one_or_none():
                    continue

                branch = Branch(
                    name=branch_name,
                    degree_id=degree.id,
                    is_active=True
                )
                session.add(branch)

        await session.commit()
        logger.success("✅ Branch seeding completed successfully")


if __name__ == "__main__":
    asyncio.run(seed_branches())
