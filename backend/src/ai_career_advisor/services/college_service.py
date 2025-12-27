from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ai_career_advisor.models.college import College


class CollegeService:

    @staticmethod
    async def get_colleges_by_state(
        db: AsyncSession,
        state: str
    ):
        result = await db.execute(
            select(College)
            .where(College.state.ilike(state))
            .order_by(College.nirf_rank.asc())
        )
        return result.scalars().all()
