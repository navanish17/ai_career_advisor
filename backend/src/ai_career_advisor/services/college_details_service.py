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
        
        def safe_get(field_key, sub_key):
            field_data = extracted.get(field_key)
            if isinstance(field_data, dict):
                return field_data.get(sub_key)
            elif sub_key == "value":
                return str(field_data) if field_data is not None else None
            return None

        details = CollegeDetails(
            college_id=college_id,
            degree=degree,
            branch=branch,

            fees_value=safe_get("fees", "value"),
            fees_source=safe_get("fees", "source"),
            fees_extracted_text=safe_get("fees", "extracted_text"),

            avg_package_value=safe_get("avg_package", "value"),
            avg_package_source=safe_get("avg_package", "source"),
            avg_package_extracted_text=safe_get("avg_package", "extracted_text"),

            highest_package_value=safe_get("highest_package", "value"),
            highest_package_source=safe_get("highest_package", "source"),
            highest_package_extracted_text=safe_get("highest_package", "extracted_text"),

            entrance_exam_value=safe_get("entrance_exam", "value"),
            entrance_exam_source=safe_get("entrance_exam", "source"),
            entrance_exam_extracted_text=safe_get("entrance_exam", "extracted_text"),

            cutoff_value=safe_get("cutoff", "value"),
            cutoff_source=safe_get("cutoff", "source"),
            cutoff_extracted_text=safe_get("cutoff", "extracted_text"),
        )

        db.add(details)
        
        logger.success(f"   ✅ Complete data cached successfully for college_id={college_id}")
        return details
