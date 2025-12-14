from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_career_advisor.models.career import Career


class CareerService:

    @staticmethod
    async def get_careers_by_branch(
        branch_id: int,
        db: AsyncSession
    ):
        result = await db.execute(
            select(Career)
            .where(
                Career.branch_id == branch_id,
                Career.is_active == True
            )
            .order_by(Career.name)
        )
        return result.scalars().all()
