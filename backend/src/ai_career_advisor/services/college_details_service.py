from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ai_career_advisor.models.college_details import CollegeDetails


class CollegeDetailsService:

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

    @staticmethod
    async def save_or_update(
        db: AsyncSession,
        *,
        college_id: int,
        degrees: list | None,
        entrance_exam: str | None,
        fees: str | None,
        avg_package: str | None,
        source_urls: list | None
    ) -> CollegeDetails:

        existing = await CollegeDetailsService.get_by_college_id(
            db, college_id
        )

        if existing:
            existing.degrees = degrees
            existing.entrance_exam = entrance_exam
            existing.fees = fees
            existing.avg_package = avg_package
            existing.source_urls = source_urls
            await db.commit()
            await db.refresh(existing)
            return existing

        details = CollegeDetails(
            college_id=college_id,
            degrees=degrees,
            entrance_exam=entrance_exam,
            fees=fees,
            avg_package=avg_package,
            source_urls=source_urls
        )

        db.add(details)
        await db.commit()
        await db.refresh(details)
        return details
