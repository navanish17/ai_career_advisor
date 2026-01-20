from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ai_career_advisor.models.career_template import CareerTemplate
from ai_career_advisor.core.logger import logger
from typing import Optional


class CareerTemplateService:
    """
    Database operations for career templates
    """
    
    @staticmethod
    async def get_by_name(
        db: AsyncSession,
        *,
        career_name: str
    ) -> Optional[CareerTemplate]:
        """
        Get template by career name
        
        Args:
            db: Database session
            career_name: Normalized career name (e.g., "Software Engineer")
        
        Returns:
            CareerTemplate object or None
        """
        result = await db.execute(
            select(CareerTemplate)
            .where(
                CareerTemplate.career_name == career_name,
                CareerTemplate.is_active == True
            )
        )
        return result.scalars().first()
    
    @staticmethod
    async def create_template(
        db: AsyncSession,
        *,
        career_name: str,
        category: str,
        roadmap_data: dict
    ) -> CareerTemplate:
        """
        Create new career template
        
        Args:
            db: Database session
            career_name: Career name
            category: Career category
            roadmap_data: Complete roadmap data
        
        Returns:
            Created CareerTemplate object
        """
        logger.info(f"   💾 Creating template for '{career_name}'...")
        
        template = CareerTemplate(
            career_name=career_name,
            category=category,
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
            is_active=True,
            version=1
        )
        
        db.add(template)
        await db.commit()
        await db.refresh(template)
        
        logger.success(f"   ✅ Template created for '{career_name}' (ID: {template.id})")
        return template
    
    @staticmethod
    async def get_all_active(
        db: AsyncSession
    ) -> list[CareerTemplate]:
        """
        Get all active templates
        
        Returns:
            List of active CareerTemplate objects
        """
        result = await db.execute(
            select(CareerTemplate)
            .where(CareerTemplate.is_active == True)
            .order_by(CareerTemplate.career_name.asc())
        )
        return result.scalars().all()
