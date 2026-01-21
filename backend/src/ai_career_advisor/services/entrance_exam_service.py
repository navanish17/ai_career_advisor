from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ai_career_advisor.models.entrance_exam import EntranceExam
from ai_career_advisor.models.college_entrance_mapping import CollegeEntranceMapping
from ai_career_advisor.core.logger import logger
from typing import Optional
from datetime import datetime, date


class EntranceExamService:
    
    @staticmethod
    async def get_or_create_from_llm(
        db: AsyncSession,
        *,
        exam_data: dict
    ) -> EntranceExam:
        
        exam_name = exam_data.get("exam_name")
        academic_year = exam_data.get("academic_year")
        
        result = await db.execute(
            select(EntranceExam).where(
                EntranceExam.exam_name == exam_name,
                EntranceExam.academic_year == str(academic_year)
            )
        )
        existing = result.scalars().first()
        
        if existing:
            logger.info(f"Exam exists in cache: {exam_name}")
            return existing
        
        logger.info(f"Creating new exam record: {exam_name}")
        
        exam = EntranceExam(
            exam_name=exam_data.get("exam_name"),
            exam_full_name=exam_data.get("exam_full_name"),
            conducting_body=exam_data.get("conducting_body"),
            exam_date=datetime.strptime(exam_data.get("exam_date"), "%Y-%m-%d").date() if exam_data.get("exam_date") else None,
            registration_start_date=datetime.strptime(exam_data.get("registration_start_date"), "%Y-%m-%d").date() if exam_data.get("registration_start_date") else None,
            registration_end_date=datetime.strptime(exam_data.get("registration_end_date"), "%Y-%m-%d").date() if exam_data.get("registration_end_date") else None,
            exam_pattern=exam_data.get("exam_pattern"),
            official_website=exam_data.get("official_website"),
            syllabus_link=exam_data.get("syllabus_link"),
            academic_year=str(exam_data.get("academic_year")),
            is_active=exam_data.get("is_active", True)
        )
        
        db.add(exam)
        await db.commit()
        await db.refresh(exam)
        
        logger.success(f"Exam saved: {exam_name} (ID: {exam.id})")
        return exam
    
    @staticmethod
    async def create_college_mapping(
        db: AsyncSession,
        *,
        college_name: str,
        degree: str,
        branch: str,
        entrance_exam_id: int
    ):
        
        result = await db.execute(
            select(CollegeEntranceMapping).where(
                CollegeEntranceMapping.college_name == college_name,
                CollegeEntranceMapping.degree == degree,
                CollegeEntranceMapping.branch == branch,
                CollegeEntranceMapping.entrance_exam_id == entrance_exam_id
            )
        )
        existing = result.scalars().first()
        
        if existing:
            return existing
        
        mapping = CollegeEntranceMapping(
            college_name=college_name,
            degree=degree,
            branch=branch,
            entrance_exam_id=entrance_exam_id
        )
        
        db.add(mapping)
        await db.commit()
        await db.refresh(mapping)
        
        return mapping
