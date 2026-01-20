from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ai_career_advisor.core.logger import logger 

from ai_career_advisor.models.college_details import CollegeDetails


class CollegeDetailsService:

    @staticmethod
    async def get_cached(
        db: AsyncSession,
        *,
        college_id: int,
        degree: str,
        branch: str
    ) -> CollegeDetails | None:
        result = await db.execute(
            select(CollegeDetails).where(
                CollegeDetails.college_id == college_id,
                CollegeDetails.degree == degree,
                CollegeDetails.branch == branch
            )
        )
        return result.scalars().first()

    @staticmethod
    async def save_from_extraction(
        db: AsyncSession,
        *,
        college_id: int,
        degree: str,
        branch: str,
        extracted: dict
    ) -> CollegeDetails | None:
        """
        Save ONLY if data is complete
        Returns None if data has errors
        """
        
        # =============================
        # CHECK FOR ERRORS
        # =============================
        if "error" in extracted:
            error_type = extracted.get("error")
            found = extracted.get("found_fields", 0)
            total = extracted.get("total_fields", 5)
            
            logger.warning(f"   ⚠️ Cannot save to cache: {error_type} ({found}/{total} fields found)")
            return None
        
        # =============================
        # CHECK IF ALREADY CACHED
        # =============================
        existing = await CollegeDetailsService.get_cached(
            db,
            college_id=college_id,
            degree=degree,
            branch=branch
        )

        if existing:
            logger.info(f"   💾 Cache already exists for college_id={college_id}")
            return existing
        
        # =============================
        # SAVE COMPLETE DATA
        # =============================
        logger.info(f"   💾 Saving complete data to cache...")
        
        details = CollegeDetails(
            college_id=college_id,
            degree=degree,
            branch=branch,

            fees_value=extracted.get("fees", {}).get("value"),
            fees_source=extracted.get("fees", {}).get("source"),
            fees_extracted_text=extracted.get("fees", {}).get("extracted_text"),

            avg_package_value=extracted.get("avg_package", {}).get("value"),
            avg_package_source=extracted.get("avg_package", {}).get("source"),
            avg_package_extracted_text=extracted.get("avg_package", {}).get("extracted_text"),

            highest_package_value=extracted.get("highest_package", {}).get("value"),
            highest_package_source=extracted.get("highest_package", {}).get("source"),
            highest_package_extracted_text=extracted.get("highest_package", {}).get("extracted_text"),

            entrance_exam_value=extracted.get("entrance_exam", {}).get("value"),
            entrance_exam_source=extracted.get("entrance_exam", {}).get("source"),
            entrance_exam_extracted_text=extracted.get("entrance_exam", {}).get("extracted_text"),

            cutoff_value=extracted.get("cutoff", {}).get("value"),
            cutoff_source=extracted.get("cutoff", {}).get("source"),
            cutoff_extracted_text=extracted.get("cutoff", {}).get("extracted_text"),
        )

        db.add(details)
        await db.commit()
        await db.refresh(details)
        
        logger.success(f"   ✅ Complete data cached successfully for college_id={college_id}")
        return details
