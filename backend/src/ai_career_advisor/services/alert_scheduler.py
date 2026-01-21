from apscheduler.schedulers.asyncio import AsyncIOScheduler
from ai_career_advisor.core.database import get_db
from ai_career_advisor.services.exam_alert_service import ExamAlertService
from ai_career_advisor.services.email_service import EmailService
from ai_career_advisor.core.logger import logger
from sqlalchemy import select
from ai_career_advisor.models.entrance_exam import EntranceExam
from datetime import date, datetime


async def send_pending_alerts():
    logger.info("Checking for pending alerts...")
    
    async for db in get_db():
        alerts = await ExamAlertService.get_pending_alerts(db, check_date=date.today())
        
        logger.info(f"Found {len(alerts)} pending alerts")
        
        for alert in alerts:
            result = await db.execute(
                select(EntranceExam).where(EntranceExam.id == alert.entrance_exam_id)
            )
            exam = result.scalars().first()
            
            if not exam:
                continue
            
            success = EmailService.send_alert_email(
                to_email=alert.user_email,
                exam_name=exam.exam_name,
                alert_type=alert.alert_type,
                target_date=str(alert.alert_date),
                exam_website=exam.official_website or "https://google.com",
                college_name=alert.college_name,
                degree=alert.degree
            )
            
            if success:
                await ExamAlertService.mark_as_sent(db, alert_id=alert.id)
                alert.sent_at = datetime.now()
                await db.commit()


def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_pending_alerts, 'cron', hour=9, minute=0)
    scheduler.start()
    logger.success("Alert scheduler started - runs daily at 9 AM")
