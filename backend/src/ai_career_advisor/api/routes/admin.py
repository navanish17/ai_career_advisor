from fastapi import APIRouter
from ai_career_advisor.services.scheduler import scheduler
from ai_career_advisor.core.logger import logger

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/reindex-knowledge-base")
async def trigger_reindex():
    logger.info("Manual re-index triggered by admin")
    scheduler.trigger_manual_reindex()
    
    return {
        "message": "Re-indexing started in background",
        "status": "processing"
    }


@router.get("/scheduler-status")
async def get_scheduler_status():
    job = scheduler.scheduler.get_job('weekly_reindex')
    
    if job:
        return {
            "status": "running",
            "next_run": job.next_run_time.isoformat(),
            "schedule": "Every Sunday 2:00 AM IST"
        }
    else:
        return {
            "status": "not_running"
        }
