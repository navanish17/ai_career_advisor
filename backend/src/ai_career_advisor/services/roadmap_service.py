from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ai_career_advisor.models.profile import Profile
from ai_career_advisor.models.degree import Degree
from ai_career_advisor.models.branch import Branch
from ai_career_advisor.models.career import Career
from ai_career_advisor.models.career_insight import CareerInsight

from ai_career_advisor.models.roadmap import Roadmap
from ai_career_advisor.models.roadmap_step import RoadmapStep


class RoadmapService:

    @staticmethod
    async def create_guided_roadmap(
        *,
        user_id: int,
        degree_id: int,
        branch_id: int,
        career_id: int,
        db: AsyncSession
    ) -> int:

        # 🔹 profile fetch
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

        # 🔹 roadmap create
        roadmap = Roadmap(
            user_id=user_id,
            class_level=profile.class_level, 
            roadmap_type="guided"
        )
        db.add(roadmap)
        await db.flush()

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
    
    @staticmethod
    async def get_roadmap(
        *,
        db: AsyncSession,
        user_id: int,
        roadmap_id: int
    ) -> dict:

        # 1️⃣ Fetch roadmap
        result = await db.execute(
            select(Roadmap).where(
                Roadmap.id == roadmap_id,
                Roadmap.user_id == user_id
            )
        )
        roadmap = result.scalars().first()

        if not roadmap:
            raise ValueError("Roadmap not found")

        # 2️⃣ Fetch profile (for class & stream)
        result = await db.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        profile = result.scalars().first()

        # 3️⃣ Fetch steps
        result = await db.execute(
            select(RoadmapStep)
            .where(RoadmapStep.roadmap_id == roadmap_id)
            .order_by(RoadmapStep.step_order)
        )
        steps = result.scalars().all()

        resolved_steps = []

        for step in steps:
            if step.step_type == "class":
                resolved_steps.append({
                    "step": "class",
                    "data": {"value": profile.class_level}
                })

            elif step.step_type == "stream":
                resolved_steps.append({
                    "step": "stream",
                    "data": {"value": profile.stream}
                })

            elif step.step_type == "degree":
                result = await db.execute(
                    select(Degree).where(Degree.id == step.reference_id)
                )
                degree = result.scalars().first()
                resolved_steps.append({
                    "step": "degree",
                    "data": {
                        "id": degree.id,
                        "name": degree.name,
                        "description": degree.short_description
                    }
                })

            elif step.step_type == "branch":
                result = await db.execute(
                    select(Branch).where(Branch.id == step.reference_id)
                )
                branch = result.scalars().first()
                resolved_steps.append({
                    "step": "branch",
                    "data": {
                        "id": branch.id,
                        "name": branch.name
                    }
                })

            elif step.step_type == "career":
                result = await db.execute(
                    select(Career).where(Career.id == step.reference_id)
                )
                career = result.scalars().first()
                resolved_steps.append({
                    "step": "career",
                    "data": {
                        "id": career.id,
                        "name": career.name,
                        "description": career.description,
                        "market_trend": career.market_trend,
                        "salary_range": career.salary_range
                    }
                })

            elif step.step_type == "top_1_percent":
                result = await db.execute(
                    select(CareerInsight).where(
                        CareerInsight.career_id == step.reference_id
                    )
                )
                insight = result.scalars().first()
                resolved_steps.append({
                    "step": "top_1_percent",
                    "data": {
                        "skills": insight.skills,
                        "projects": insight.projects,
                        "internships": insight.internships,
                        "programs": insight.programs
                    }
                })

        return {
            "roadmap_id": roadmap.id,
            "class_level": roadmap.class_level,
            "steps": resolved_steps
        }
