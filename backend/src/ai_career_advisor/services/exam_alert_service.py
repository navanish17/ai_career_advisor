from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from ai_career_advisor.models.exam_alert import ExamAlert
from ai_career_advisor.models.entrance_exam import EntranceExam
from ai_career_advisor.core.logger import logger
from datetime import date, timedelta
from typing import List


class ExamAlertService:
    
    @staticmethod
    async def create_alert(
        db: AsyncSession,
        *,
        user_email: str,
        entrance_exam_id: int,
        alert_type: str,
        target_date: date,
        college_name: str = None,
        degree: str = None,
        branch: str = None
    ) -> ExamAlert:
        
        alert_date = target_date
        
        result = await db.execute(
            select(ExamAlert).where(
                and_(
                    ExamAlert.user_email == user_email,
                    ExamAlert.entrance_exam_id == entrance_exam_id,
                    ExamAlert.alert_type == alert_type,
                    ExamAlert.is_sent == False
                )
            )
        )
        existing = result.scalars().first()
        
        if existing:
            logger.info(f"Alert already exists for {user_email} - {alert_type}")
            return existing
        
        alert = ExamAlert(
            user_email=user_email,
            entrance_exam_id=entrance_exam_id,
            alert_type=alert_type,
            alert_date=alert_date,
            college_name=college_name,
            degree=degree,
            branch=branch,
            is_sent=False
        )
        
        db.add(alert)
        await db.commit()
        await db.refresh(alert)
        
        logger.success(f"Alert created: {alert_type} for {user_email}")
        return alert
    
    @staticmethod
    async def get_pending_alerts(
        db: AsyncSession,
        *,
        check_date: date = None
    ) -> List[ExamAlert]:
        
        if not check_date:
            check_date = date.today()
        
        result = await db.execute(
            select(ExamAlert).where(
                and_(
                    ExamAlert.alert_date <= check_date,
                    ExamAlert.is_sent == False
                )
            )
        )
        
        return result.scalars().all()
    
    @staticmethod
    async def mark_as_sent(
        db: AsyncSession,
        *,
        alert_id: int
    ):
        
        result = await db.execute(
            select(ExamAlert).where(ExamAlert.id == alert_id)
        )
        alert = result.scalars().first()
        
        if alert:
            alert.is_sent = True
            await db.commit()
