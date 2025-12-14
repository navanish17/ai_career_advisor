from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_career_advisor.models.branch import Branch
from ai_career_advisor.core.logger import logger


class BranchService:

    @staticmethod
    async def get_branches_by_degree(
        db: AsyncSession,
        degree_id: int
    ):
        logger.info(f"Fetching branches for degree_id={degree_id}")

        result = await db.execute(
            select(Branch)
            .where(
                Branch.degree_id == degree_id,
                Branch.is_active == True
            )
            .order_by(Branch.name)
        )

        branches = result.scalars().all()

        logger.info(
            f"Found {len(branches)} branches for degree_id={degree_id}"
        )

        return branches
