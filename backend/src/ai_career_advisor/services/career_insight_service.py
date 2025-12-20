from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_career_advisor.models.career_insight import CareerInsight


class CareerInsightService:

    @staticmethod
    async def get_by_career_id(
        career_id: int,
        db: AsyncSession
    ):
        result = await db.execute(
            select(CareerInsight)
            .where(CareerInsight.career_id == career_id)
        )
        return result.scalar_one_or_none()
