from sqlalchemy.ext.asyncio import AsyncSession

from ai_career_advisor.models.roadmap import Roadmap
from ai_career_advisor.models.roadmap_step import RoadmapStep


class RoadmapService:

    @staticmethod
    async def create_guided_roadmap(
        *,
        user_id: int,
        class_level: str,
        degree_id: int,
        branch_id: int,
        career_id: int,
        db: AsyncSession
    ) -> int:

        roadmap = Roadmap(
            user_id=user_id,
            class_level=class_level,
            roadmap_type="guided"
        )
        db.add(roadmap)
        await db.flush()

        steps = [
            {"order": 1, "type": "class", "table": None, "ref": None},
            {"order": 2, "type": "stream", "table": None, "ref": None},
            {"order": 3, "type": "degree", "table": "degree", "ref": degree_id},
            {"order": 4, "type": "branch", "table": "branch", "ref": branch_id},
            {"order": 5, "type": "career", "table": "career", "ref": career_id},
            {"order": 6, "type": "top_1_percent", "table": "career_insight", "ref": career_id},
        ]

        for s in steps:
            step = RoadmapStep(
                roadmap_id=roadmap.id,
                step_order=s["order"],
                step_type=s["type"],
                reference_table=s["table"],
                reference_id=s["ref"]
            )
            db.add(step)

        await db.commit()
        return roadmap.id
