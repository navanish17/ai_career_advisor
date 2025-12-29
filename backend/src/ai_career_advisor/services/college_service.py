from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ai_career_advisor.models.college import College


class CollegeService:
    
    @staticmethod
    async def get_top_colleges_by_state(
        db: AsyncSession,
        *,
        state: str,
        top_n: int = 100
    ):
        result = await db.execute(
            select(College)
            .where(
                College.state.ilike(state),
                College.nirf_rank.isnot(None),
                College.nirf_rank <= top_n
            )
            .order_by(College.nirf_rank.asc())
        )
        return result.scalars().all()
