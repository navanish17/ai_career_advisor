from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_career_advisor.models.career_insight import CareerInsight
from ai_career_advisor.services.career_insight_llm import generate_career_insight  
from ai_career_advisor.core.logger import logger  


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

    
    @staticmethod
    async def generate_and_save(
        career_id: int,
        career_name: str,
        db: AsyncSession
    ) -> CareerInsight:
        """
        Generate career insight using LLM and save to database
        """
        try:
            logger.info(f"🔄 Generating insight for career: {career_name} (ID: {career_id})")
            
            
            data = await generate_career_insight(career_name)
            
            
            insight = CareerInsight(
                career_id=career_id,
                skills=data["skills"],
                internships=data["internships"],
                projects=data["projects"],
                programs=data["programs"],
                top_salary=data.get("top_salary"),
                is_active=True
            )
            
            db.add(insight)
            await db.commit()
            await db.refresh(insight)
            
            logger.success(f"✅ Insight saved for {career_name}")
            return insight
            
        except Exception as e:
            logger.error(f"❌ Failed to generate insight for {career_name}: {e}")
            await db.rollback()
            raise
