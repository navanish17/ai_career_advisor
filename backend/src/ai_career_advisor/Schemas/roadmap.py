from pydantic import BaseModel

class RoadmapGenerateRequest(BaseModel):
    degree_id: int
    branch_id: int
    career_id: int


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ai_career_advisor.models.profile import Profile
from ai_career_advisor.models.roadmap import Roadmap
from ai_career_advisor.models.roadmap_step import RoadmapStep


class RoadmapService:

    @staticmethod
    async def generate_roadmap(
        *,
        db: AsyncSession,
        user_id: int,
        degree_id: int,
        branch_id: int,
        career_id: int
    ) -> int:

        # 1️⃣ Fetch profile
        result = await db.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        profile = result.scalars().first()

        if not profile:
            raise ValueError("Profile not found")

        if not profile.class_level:
            raise ValueError("Class level not set")

        if not profile.stream:
            raise ValueError("Stream not set")

        # 2️⃣ Create roadmap
        roadmap = Roadmap(
            user_id=user_id,
            class_level=profile.class_level,
            roadmap_type="guided"
        )
        db.add(roadmap)
        await db.flush()  # roadmap.id available

        # 3️⃣ Create steps (ORDERED & LOCKED)
        steps = [
            ("class", None, None),
            ("stream", None, None),
            ("degree", "degree", degree_id),
            ("branch", "branch", branch_id),
            ("career", "career", career_id),
            ("top_1_percent", "career_insight", career_id),
        ]

        for order, (step_type, table, ref_id) in enumerate(steps, start=1):
            db.add(
                RoadmapStep(
                    roadmap_id=roadmap.id,
                    step_order=order,
                    step_type=step_type,
                    reference_table=table,
                    reference_id=ref_id
                )
            )

        await db.commit()
        return roadmap.id
