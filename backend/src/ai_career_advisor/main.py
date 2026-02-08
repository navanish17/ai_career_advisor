from ai_career_advisor.app import create_app 
from ai_career_advisor.core.logger import logger
from ai_career_advisor.api.routes import *
from ai_career_advisor.services.alert_scheduler import start_scheduler

app = create_app()


app.include_router(degree_router)     
app.include_router(branch)            
app.include_router(career)            


app.include_router(auth, prefix="/api/auth")
app.include_router(profile, prefix="/api/profile")
app.include_router(quiz, prefix="/api/quiz")
app.include_router(roadmap, prefix="/api/roadmap")
app.include_router(scholarships, prefix="/api/scholarships")
app.include_router(agent, prefix="/api/agent")
app.include_router(college_router, prefix="/api")


app.include_router(admin_router)
app.include_router(admission_alerts_router)
app.include_router(backward_planner_router)
app.include_router(career_insight)
app.include_router(chatbot_router)
app.include_router(intent_router, prefix="/api")
app.include_router(recommendations_router, prefix="/api")

@app.get('/health')
async def health_check():
    logger.info("health checking")
    return {
        "status": 'ok',
        "message": "Backend running succesfully ✅"
    }

@app.on_event("startup")
async def startup_event():
    start_scheduler()
