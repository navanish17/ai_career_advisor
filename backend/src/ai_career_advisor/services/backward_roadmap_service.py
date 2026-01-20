from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ai_career_advisor.models.backward_roadmap import BackwardRoadmap
from ai_career_advisor.core.logger import logger
from typing import Optional


class BackwardRoadmapService:
    """
    Database operations for backward roadmaps
    """
    
    @staticmethod
    async def get_by_career(
        db: AsyncSession,
        *,
        career_name: str
    ) -> Optional[BackwardRoadmap]:
        """
        Get existing roadmap by normalized career name
        
        Args:
            db: Database session
            career_name: Normalized career name (e.g., "Software Engineer")
        
        Returns:
            BackwardRoadmap object or None
        """
        result = await db.execute(
            select(BackwardRoadmap)
            .where(BackwardRoadmap.normalized_career == career_name)
            .order_by(BackwardRoadmap.created_at.desc())
            .limit(1)
        )
        return result.scalars().first()
    
    @staticmethod
    async def create_from_llm(
        db: AsyncSession,
        *,
        career_goal_input: str,
        normalized_career: str,
        category: str,
        roadmap_data: dict,
        user_id: Optional[int] = None
    ) -> BackwardRoadmap:
        """
        Create new roadmap from LLM-generated data
        
        Args:
            db: Database session
            career_goal_input: Raw user input
            normalized_career: Standardized career name
            category: Career category
            roadmap_data: Generated roadmap dict from LLM
            user_id: Optional user ID
        
        Returns:
            Created BackwardRoadmap object
        """
        logger.info(f"   💾 Saving LLM-generated roadmap to database...")
        
        roadmap = BackwardRoadmap(
            user_id=user_id,
            career_goal_input=career_goal_input,
            normalized_career=normalized_career,
            career_category=category,
            career_description=roadmap_data.get("career_description"),
            required_education=roadmap_data.get("required_education"),
            entrance_exams=roadmap_data.get("entrance_exams"),
            stream_recommendation=roadmap_data.get("stream_recommendation"),
            skills_required=roadmap_data.get("skills_required"),
            projects_to_build=roadmap_data.get("projects_to_build"),
            internships=roadmap_data.get("internships"),
            certifications=roadmap_data.get("certifications"),
            top_colleges=roadmap_data.get("top_colleges"),
            career_prospects=roadmap_data.get("career_prospects"),
            timeline=roadmap_data.get("timeline"),
            source="llm_generated",
            confidence_score=0.85  # Default confidence for LLM generation
        )
        
        db.add(roadmap)
        await db.commit()
        await db.refresh(roadmap)
        
        logger.success(f"   ✅ Roadmap saved to database (ID: {roadmap.id})")
        return roadmap
    
    @staticmethod
    async def create_from_template(
        db: AsyncSession,
        *,
        career_goal_input: str,
        normalized_career: str,
        category: str,
        template_data: dict,
        user_id: Optional[int] = None
    ) -> BackwardRoadmap:
        """
        Create roadmap from pre-built template
        
        Args:
            db: Database session
            career_goal_input: Raw user input
            normalized_career: Standardized career name
            category: Career category
            template_data: Template dict
            user_id: Optional user ID
        
        Returns:
            Created BackwardRoadmap object
        """
        logger.info(f"   💾 Saving template-based roadmap to database...")
        
        roadmap = BackwardRoadmap(
            user_id=user_id,
            career_goal_input=career_goal_input,
            normalized_career=normalized_career,
            career_category=category,
            career_description=template_data.get("career_description"),
            required_education=template_data.get("required_education"),
            entrance_exams=template_data.get("entrance_exams"),
            stream_recommendation=template_data.get("stream_recommendation"),
            skills_required=template_data.get("skills_required"),
            projects_to_build=template_data.get("projects_to_build"),
            internships=template_data.get("internships"),
            certifications=template_data.get("certifications"),
            top_colleges=template_data.get("top_colleges"),
            career_prospects=template_data.get("career_prospects"),
            timeline=template_data.get("timeline"),
            source="template",
            confidence_score=1.0  # Templates are verified, so high confidence
        )
        
        db.add(roadmap)
        await db.commit()
        await db.refresh(roadmap)
        
        logger.success(f"   ✅ Template roadmap saved (ID: {roadmap.id})")
        return roadmap
