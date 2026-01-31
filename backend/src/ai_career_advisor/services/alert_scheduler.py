from apscheduler.schedulers.asyncio import AsyncIOScheduler
from ai_career_advisor.core.database import get_db
from ai_career_advisor.services.exam_alert_service import ExamAlertService
from ai_career_advisor.services.brevo_service import BrevoService
from ai_career_advisor.core.logger import logger
from sqlalchemy import select
from ai_career_advisor.models.entrance_exam import EntranceExam
from datetime import date, datetime


async def send_pending_alerts():
    logger.info("🔍 Checking for pending alerts...")
    
    async for db in get_db():
        alerts = await ExamAlertService.get_pending_alerts(db, check_date=date.today())
        
        logger.info(f"📧 Found {len(alerts)} pending alerts")
        
        sent_count = 0
        failed_count = 0
        
        for alert in alerts:
            result = await db.execute(
                select(EntranceExam).where(EntranceExam.id == alert.entrance_exam_id)
            )
            exam = result.scalars().first()
            
            if not exam:
                logger.warning(f"⚠️ Exam not found for alert {alert.id}")
                continue
            
            # Determine target date based on alert type
            target_date = _get_target_date(alert.alert_type, exam)
            
            # Send email via Brevo
            success = await BrevoService.send_admission_alert(
                to_email=alert.user_email,
                exam_name=exam.exam_name,
                college_name=alert.college_name or "Your Selected College",
                degree=alert.degree or "",
                branch=alert.branch or "",
                alert_type=alert.alert_type,
                target_date=target_date,
                exam_details={
                    "official_website": exam.official_website,
                    "conducting_body": exam.conducting_body,
                    "exam_pattern": exam.exam_pattern,
                    "syllabus_link": exam.syllabus_link
                }
            )
            
            if success:
                await ExamAlertService.mark_as_sent(db, alert_id=alert.id)
                alert.sent_at = datetime.now()
                sent_count += 1
                logger.success(f"✅ Sent {alert.alert_type} alert to {alert.user_email}")
            else:
                failed_count += 1
                logger.error(f"❌ Failed to send alert to {alert.user_email}")
        
        await db.commit()
        logger.info(f"📊 Alert sending complete: {sent_count} sent, {failed_count} failed")
        break  # Exit the async generator


def _get_target_date(alert_type: str, exam: EntranceExam) -> datetime:
    """Get the target date for an alert based on type"""
    if alert_type == "registration_start":
        return exam.registration_start_date or exam.exam_date
    elif alert_type in ["registration_3days", "registration_last"]:
        return exam.registration_end_date or exam.exam_date
    elif alert_type == "exam_1day":
        return exam.exam_date
    else:
        return exam.exam_date or datetime.now()



def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_pending_alerts, 'cron', hour=9, minute=0)
    scheduler.start()
    logger.success("Alert scheduler started - runs daily at 9 AM")
