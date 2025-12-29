from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ai_career_advisor.models.college_details import CollegeDetails


class CollegeDetailsService:

    # 🔹 STEP 2.1 — CACHE CHECK
    @staticmethod
    async def get_cached(
        db: AsyncSession,
        *,
        college_id: int,
        degree: str,
        branch: str
    ) -> CollegeDetails | None:
        result = await db.execute(
            select(CollegeDetails).where(
                CollegeDetails.college_id == college_id,
                CollegeDetails.degree == degree,
                CollegeDetails.branch == branch
            )
        )
        return result.scalars().first()
    
    @staticmethod
    async def get_by_college_id(
        db: AsyncSession,
        college_id: int
    ) -> CollegeDetails | None:
        result = await db.execute(
            select(CollegeDetails)
            .where(CollegeDetails.college_id == college_id)
        )
        return result.scalars().first()

    # 🔹 STEP 2.2 — SAVE STRICT GEMINI OUTPUT
    @staticmethod
    async def save_from_extraction(
        db: AsyncSession,
        *,
        college_id: int,
        degree: str,
        branch: str,
        extracted: dict
    ) -> CollegeDetails:

        existing = await CollegeDetailsService.get_cached(
            db,
            college_id=college_id,
            degree=degree,
            branch=branch
        )

        if existing:
            return existing  # cache already exists (NO overwrite)

        details = CollegeDetails(
            college_id=college_id,
            degree=degree,
            branch=branch,

            fees_value=extracted["fees"]["value"],
            fees_source=extracted["fees"]["source"],
            fees_extracted_text=extracted["fees"]["extracted_text"],

            avg_package_value=extracted["avg_package"]["value"],
            avg_package_source=extracted["avg_package"]["source"],
            avg_package_extracted_text=extracted["avg_package"]["extracted_text"],

            highest_package_value=extracted["highest_package"]["value"],
            highest_package_source=extracted["highest_package"]["source"],
            highest_package_extracted_text=extracted["highest_package"]["extracted_text"],

            entrance_exam_value=extracted["entrance_exam"]["value"],
            entrance_exam_source=extracted["entrance_exam"]["source"],
            entrance_exam_extracted_text=extracted["entrance_exam"]["extracted_text"],

            cutoff_value=extracted["cutoff"]["value"],
            cutoff_source=extracted["cutoff"]["source"],
            cutoff_extracted_text=extracted["cutoff"]["extracted_text"],
        )

        db.add(details)
        await db.commit()
        await db.refresh(details)
        return details
