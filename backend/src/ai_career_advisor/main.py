from ai_career_advisor.app import create_app 
from ai_career_advisor.core.logger import logger
from ai_career_advisor.api.routes import agent, auth, career, colleges, profile,quiz,roadmap,scholarships




app = create_app()

#include routers

app.include_router(auth.router, prefix = "/api/auth")
app.include_router(agent.router, prefix = "/api/agent")
app.include_router(career.router, prefix = "/api/career")
app.include_router(colleges.router, prefix = "/api/colleges")
app.include_router(profile.router, prefix = "/api/profile")
app.include_router(quiz.router, prefix = "/api/quiz")
app.include_router(roadmap.router, prefix = "/api/roadmap")
app.include_router(scholarships.router, prefix = "/api/scholarships")

@app.get('/health')
async def health_check():
    logger.info("health checking")
    return {
        "status": 'ok',
        "message": "Backend running succesfully ✅"
    }
