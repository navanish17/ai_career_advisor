from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ai_career_advisor.core.database import get_db
from ai_career_advisor.core.logger import logger
from ai_career_advisor.Schemas.admission_alerts import (
    EntranceExamSearchRequest,
    CreateAlertRequest,
    AdmissionAlertSuccessResponse,
    EntranceExamResponse,
    AlertResponse
)

from ai_career_advisor.services.entrance_exam_llm import EntranceExamLLM
from ai_career_advisor.services.entrance_exam_service import EntranceExamService
from ai_career_advisor.services.exam_alert_service import ExamAlertService
from datetime import datetime


router = APIRouter(prefix="/admission-alerts", tags=["Admission Alerts"])


@router.post("/search-exam", response_model=AdmissionAlertSuccessResponse)
async def search_entrance_exam(
    payload: EntranceExamSearchRequest,
    db: AsyncSession = Depends(get_db)
):
    
    logger.info(f"Search exam: {payload.college_name} - {payload.degree}")
    
    exam_data = await EntranceExamLLM.get_entrance_exam_info(
        college_name=payload.college_name,
        degree=payload.degree,
        branch=payload.branch
    )
    
    if "error" in exam_data:
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to fetch exam data", "message": exam_data.get("error")}
        )
    
    exam = await EntranceExamService.get_or_create_from_llm(db, exam_data=exam_data)
    
    await EntranceExamService.create_college_mapping(
        db,
        college_name=payload.college_name,
        degree=payload.degree,
        branch=payload.branch or "",
        entrance_exam_id=exam.id
    )
    
    return AdmissionAlertSuccessResponse(
        success=True,
        message=f"Found entrance exam: {exam.exam_name}",
        exam=EntranceExamResponse(**exam.to_dict())
    )


@router.post("/set-alert", response_model=AdmissionAlertSuccessResponse)
async def set_exam_alert(
    payload: CreateAlertRequest,
    db: AsyncSession = Depends(get_db)
):
    
    logger.info(f"Creating alerts for {payload.user_email}")
    
    exam_data = await EntranceExamLLM.get_entrance_exam_info(
        college_name=payload.college_name,
        degree=payload.degree,
        branch=payload.branch
    )
    
    if "error" in exam_data:
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to fetch exam data"}
        )
    
    exam = await EntranceExamService.get_or_create_from_llm(db, exam_data=exam_data)
    
    from datetime import timedelta
    
    alert_configs = {
        "registration_start": {
            "target_date": exam.registration_start_date,
            "days_before": 0,
            "description": "Registration opens"
        },
        "registration_3days": {
            "target_date": exam.registration_end_date,
            "days_before": 3,
            "description": "3 days before registration closes"
        },
        "registration_last": {
            "target_date": exam.registration_end_date,
            "days_before": 1,
            "description": "Last day of registration"
        },
        "exam_1day": {
            "target_date": exam.exam_date,
            "days_before": 1,
            "description": "1 day before exam"
        }
    }
    
    created_alerts = []
    
    # If no dates found, create a "General" update alert
    if not any(config["target_date"] for config in alert_configs.values()):
        logger.warning("No specific dates found, creating general alert")
        # Set a default check-in date 30 days from now
        alert = await ExamAlertService.create_alert(
            db,
            user_email=payload.user_email,
            entrance_exam_id=exam.id,
            alert_type="general_update",
            target_date=datetime.now().date() + timedelta(days=30),
            college_name=payload.college_name,
            degree=payload.degree,
            branch=payload.branch
        )
        created_alerts.append(alert)
    else:
        for alert_type in payload.alert_types:
            if alert_type not in alert_configs:
                continue
            
            config = alert_configs[alert_type]
            target_date = config["target_date"]
            
            if not target_date:
                logger.warning(f"Skipping {alert_type} - date not available")
                continue
            
            # Ensure target_date is a date object
            if isinstance(target_date, str):
                 try:
                     target_date = datetime.strptime(target_date, "%Y-%m-%d").date()
                 except ValueError:
                     logger.error(f"Invalid date format: {target_date}")
                     continue

            alert_date = target_date - timedelta(days=config["days_before"])
            
            alert = await ExamAlertService.create_alert(
                db,
                user_email=payload.user_email,
                entrance_exam_id=exam.id,
                alert_type=alert_type,
                target_date=target_date,
                college_name=payload.college_name,
                degree=payload.degree,
                branch=payload.branch
            )
            
            created_alerts.append(alert)
    
    # Send confirmation email via Brevo
    if created_alerts:
        from ai_career_advisor.services.brevo_service import BrevoService
        
        # Send a confirmation email for the first alert
        first_alert = created_alerts[0]
        await BrevoService.send_admission_alert(
            to_email=payload.user_email,
            exam_name=exam.exam_name,
            college_name=payload.college_name,
            degree=payload.degree,
            branch=payload.branch or "",
            alert_type="registration_start",  # Confirmation email
            target_date=exam.registration_start_date or exam.exam_date,
            exam_details={
                "official_website": exam.official_website,
                "conducting_body": exam.conducting_body,
                "exam_pattern": exam.exam_pattern,
                "syllabus_link": exam.syllabus_link
            }
        )
    
    return AdmissionAlertSuccessResponse(
        success=True,
        message=f"Created {len(created_alerts)} alerts successfully",
        exam=EntranceExamResponse(**exam.to_dict()),
        alert=AlertResponse(**created_alerts[0].to_dict()) if created_alerts else None
    )


@router.get("/my-alerts")
async def get_my_alerts(
    email: str,
    db: AsyncSession = Depends(get_db)
):
    
    from sqlalchemy import select
    from ai_career_advisor.models.exam_alert import ExamAlert
    
    result = await db.execute(
        select(ExamAlert).where(ExamAlert.user_email == email)
    )
    alerts = result.scalars().all()
    
    return {
        "success": True,
        "count": len(alerts),
        "alerts": [AlertResponse(**alert.to_dict()) for alert in alerts]
    }


@router.post("/test-email")
async def test_brevo_email(email: str):
    """Test endpoint to verify Brevo email integration"""
    from ai_career_advisor.services.brevo_service import BrevoService
    from datetime import datetime, timedelta
    
    logger.info(f"📧 Sending test email to {email}")
    
    success = await BrevoService.send_admission_alert(
        to_email=email,
        exam_name="JEE Main 2026",
        college_name="IIT Bombay",
        degree="B.Tech",
        branch="Computer Science",
        alert_type="registration_start",
        target_date=datetime.now() + timedelta(days=30),
        exam_details={
            "official_website": "https://jeemain.nta.nic.in",
            "conducting_body": "National Testing Agency (NTA)",
            "exam_pattern": "Computer Based Test (CBT)",
            "syllabus_link": "https://jeemain.nta.nic.in/syllabus"
        }
    )
    
    if success:
        return {
            "success": True,
            "message": f"Test email sent successfully to {email}. Check your inbox!"
        }
    else:
        return {
            "success": False,
            "message": "Failed to send test email. Check BREVO_API_KEY in .env file"
        }
