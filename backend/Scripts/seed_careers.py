import asyncio
from sqlalchemy import select

from ai_career_advisor.core.database import AsyncSessionLocal
from ai_career_advisor.models.branch import Branch
from ai_career_advisor.models.career import Career
from ai_career_advisor.core.logger import logger


CAREERS = {
    # ---------- SCIENCE ----------
    "Computer / Software": [
        "Software Engineer",
        "Cloud Engineer",
        "Cybersecurity Engineer",
        "Data Engineer",
        "AI/ML Engineer",
    ],
    "Mechanical / Manufacturing": [
        "Mechanical Engineer",
        "Production Engineer",
        "Maintenance Engineer",
        "Design Engineer",
        "Quality Engineer",
    ],
    "Civil / Infrastructure": [
        "Civil Engineer",
        "Site Engineer",
        "Structural Engineer",
        "Project Engineer",
        "Quantity Surveyor",
    ],
    "Electrical / Electronics": [
        "Electrical Engineer",
        "Electronics Engineer",
        "Power Systems Engineer",
        "Control Systems Engineer",
        "Instrumentation Engineer",
    ],
    "Chemical / Process": [
        "Chemical Engineer",
        "Process Engineer",
        "Production Chemist",
        "Quality Control Engineer",
        "Safety Engineer",
    ],

    "Physics": [
        "Research Assistant",
        "Lab Scientist",
        "Physics Analyst",
        "Scientific Officer",
        "Teaching Assistant",
    ],
    "Chemistry": [
        "Chemist",
        "Quality Control Analyst",
        "Research Chemist",
        "Lab Analyst",
        "Chemical Technician",
    ],
    "Mathematics": [
        "Data Analyst",
        "Statistical Analyst",
        "Operations Analyst",
        "Research Assistant",
        "Teaching Assistant",
    ],
    "Biology": [
        "Biologist",
        "Lab Technician",
        "Research Assistant",
        "Clinical Data Associate",
        "Biomedical Analyst",
    ],

    "Software Development": [
        "Software Developer",
        "Web Developer",
        "Application Developer",
        "Backend Developer",
        "Junior Full Stack Developer",
    ],
    "Data & Analytics": [
        "Data Analyst",
        "Business Analyst",
        "Reporting Analyst",
        "Junior Data Scientist",
        "MIS Analyst",
    ],
    "Cybersecurity": [
        "Cybersecurity Analyst",
        "SOC Analyst",
        "Information Security Analyst",
        "Security Operations Executive",
        "Vulnerability Analyst",
    ],

    "Clinical Medicine": [
        "General Physician",
        "Medical Officer",
        "Resident Doctor",
        "Clinical Associate",
        "Hospital Medical Officer",
    ],
    "Surgery": [
        "Junior Surgeon",
        "Surgical Resident",
        "Assistant Surgeon",
        "Trauma Care Doctor",
        "Surgical Medical Officer",
    ],
    "Diagnostics & Public Health": [
        "Public Health Officer",
        "Epidemiology Assistant",
        "Clinical Research Associate",
        "Medical Data Analyst",
        "Health Program Officer",
    ],

    # ---------- ARTS ----------
    "Humanities": [
        "Content Executive",
        "Research Assistant",
        "Policy Assistant",
        "Academic Coordinator",
        "Documentation Officer",
    ],
    "Social Sciences": [
        "Social Research Assistant",
        "Program Coordinator",
        "Survey Analyst",
        "Development Executive",
        "NGO Project Officer",
    ],
    "Languages": [
        "Content Writer",
        "Translator",
        "Editorial Assistant",
        "Language Trainer",
        "Communication Executive",
    ],

    "Fine Arts": [
        "Visual Artist",
        "Illustrator",
        "Art Instructor",
        "Creative Assistant",
        "Studio Artist",
    ],
    "Visual Design": [
        "Graphic Designer",
        "Visual Designer",
        "Branding Executive",
        "Creative Designer",
        "Design Associate",
    ],
    "Performing Arts": [
        "Performing Artist",
        "Theatre Practitioner",
        "Choreography Assistant",
        "Cultural Program Coordinator",
        "Arts Facilitator",
    ],

    # ---------- COMMERCE ----------
    "Accounting": [
        "Accountant",
        "Accounts Executive",
        "Junior Auditor",
        "Billing & Invoicing Executive",
        "Accounts Assistant",
    ],
    "Finance": [
        "Financial Analyst (Junior)",
        "Finance Executive",
        "Credit Analyst",
        "Treasury Assistant",
        "Investment Support Executive",
    ],
    "Banking & Insurance": [
        "Banking Executive",
        "Insurance Officer",
        "Relationship Officer",
        "Operations Executive",
        "Claims Processing Executive",
    ],
}


async def seed_careers():
    async with AsyncSessionLocal() as session:
        for branch_name, career_list in CAREERS.items():

            result = await session.execute(
                select(Branch).where(Branch.name == branch_name)
            )
            branch = result.scalar_one_or_none()

            if not branch:
                logger.warning(f"Branch not found: {branch_name}")
                continue

            for career_name in career_list:
                exists = await session.execute(
                    select(Career).where(
                        Career.name == career_name,
                        Career.branch_id == branch.id,
                    )
                )
                if exists.scalar_one_or_none():
                    continue

                career = Career(
                    name=career_name,
                    branch_id=branch.id,
                    is_active=True,
                )
                session.add(career)

        await session.commit()
        logger.success("✅ Career seeding completed successfully")


if __name__ == "__main__":
    asyncio.run(seed_careers())
