from ai_career_advisor.app import create_app 
from ai_career_advisor.core.logger import logger
from ai_career_advisor.api.routes import agent, auth,degree_router, career, colleges, profile,quiz,roadmap,scholarships,branch
import ai_career_advisor.models






app = create_app()

#include routers

app.include_router(auth, prefix="/api/auth")
app.include_router(agent, prefix="/api/agent")
app.include_router(career, prefix="/api/career")
app.include_router(colleges, prefix="/api/colleges")
app.include_router(profile, prefix="/api/profile")
app.include_router(quiz, prefix="/api/quiz")
app.include_router(branch)
app.include_router(degree_router, prefix="/api/degree")
app.include_router(roadmap, prefix="/api/roadmap")
app.include_router(scholarships, prefix="/api/scholarships")

@app.get('/health')
async def health_check():
    logger.info("health checking")
    return {
        "status": 'ok',
        "message": "Backend running succesfully ✅"
    }
