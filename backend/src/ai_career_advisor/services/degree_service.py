from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ai_career_advisor.models.degree import Degree
from ai_career_advisor.Schemas.degree import DegreeCreate


class DegreeService:

    @staticmethod
    async def get_all_degrees(db: AsyncSession):
        """Return all active degrees."""
        query = select(Degree).where(Degree.is_active == True)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_degrees_by_stream(db: AsyncSession, stream: str):
        """Return all degrees for a given stream."""
        query = select(Degree).where(
            Degree.stream == stream,
            Degree.is_active == True
        )
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def create_degree(db: AsyncSession, degree_data: DegreeCreate):
        """Create new degree (used in seeding or admin)."""
        new_degree = Degree(**degree_data.dict())
        db.add(new_degree)
        await db.commit()
        await db.refresh(new_degree)
        return new_degree
