from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ai_career_advisor.core.logger import logger
from ai_career_advisor.core.config import settings

# Create app directly without lifespan for now
app = FastAPI(
    title="AI Career Advisor API",
    debug=settings.DEBUG,
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import only ESSENTIAL routes that we know work
try:
    from ai_career_advisor.api.routes.auth import router as auth
    app.include_router(auth, prefix="/api/auth")
    logger.info("✓ Auth router loaded")
except Exception as e:
    logger.error(f"✗ Auth router failed: {e}")

try:
    from ai_career_advisor.api.routes.chatbot import router as chatbot_router
    app.include_router(chatbot_router, prefix="/api/chatbot")
    logger.info("✓ Chatbot router loaded")
except Exception as e:
    logger.error(f"✗ Chatbot router failed: {e}")

try:
    from ai_career_advisor.api.routes.profile import router as profile
    app.include_router(profile, prefix="/api/profile")
    logger.info("✓ Profile router loaded")
except Exception as e:
    logger.error(f"✗ Profile router failed: {e}")

try:
    from ai_career_advisor.api.routes.roadmap import router as roadmap
    app.include_router(roadmap, prefix="/api/roadmap")
    logger.info("✓ Roadmap router loaded")
except Exception as e:
    logger.error(f"✗ Roadmap router failed: {e}")

try:
    from ai_career_advisor.api.routes.colleges import router as college_router
    app.include_router(college_router, prefix="/api")
    logger.info("✓ Colleges router loaded")
except Exception as e:
    logger.error(f"✗ Colleges router failed: {e}")

try:
    from ai_career_advisor.api.routes.quiz import router as quiz
    app.include_router(quiz, prefix="/api/quiz")
    logger.info("✓ Quiz router loaded")
except Exception as e:
    logger.error(f"✗ Quiz router failed: {e}")

try:
    from ai_career_advisor.api.routes.scholarships import router as scholarships
    app.include_router(scholarships, prefix="/api/scholarships")
    logger.info("✓ Scholarships router loaded")
except Exception as e:
    logger.error(f"✗ Scholarships router failed: {e}")

try:
    from ai_career_advisor.api.routes.agent import router as agent
    app.include_router(agent, prefix="/api/agent")
    logger.info("✓ Agent router loaded")
except Exception as e:
    logger.error(f"✗ Agent router failed: {e}")

try:
    from ai_career_advisor.api.routes.degree import router as degree_router
    app.include_router(degree_router, prefix="/api/degrees")
    logger.info("✓ Degree router loaded")
except Exception as e:
    logger.error(f"✗ Degree router failed: {e}")

try:
    from ai_career_advisor.api.routes.branch import router as branch
    app.include_router(branch, prefix="/api/branches")
    logger.info("✓ Branch router loaded")
except Exception as e:
    logger.error(f"✗ Branch router failed: {e}")

try:
    from ai_career_advisor.api.routes.career import router as career
    app.include_router(career, prefix="/api/careers")
    logger.info("✓ Career router loaded")
except Exception as e:
    logger.error(f"✗ Career router failed: {e}")

try:
    from ai_career_advisor.api.routes.admission_alerts import router as admission_alerts_router
    app.include_router(admission_alerts_router, prefix="/api/admission-alerts")
    logger.info("✓ Admission Alerts router loaded")
except Exception as e:
    logger.error(f"✗ Admission Alerts router failed: {e}")

try:
    from ai_career_advisor.api.routes.backward_planner import router as backward_planner_router
    app.include_router(backward_planner_router, prefix="/api/backward-planner")
    logger.info("✓ Backward Planner router loaded")
except Exception as e:
    logger.error(f"✗ Backward Planner router failed: {e}")

try:
    from ai_career_advisor.api.routes.career_insight import router as career_insight
    app.include_router(career_insight, prefix="/api/career-insight")
    logger.info("✓ Career Insight router loaded")
except Exception as e:
    logger.error(f"✗ Career Insight router failed: {e}")

try:
    from ai_career_advisor.api.routes.recommendations import router as recommendations_router
    app.include_router(recommendations_router, prefix="/api/recommendations")
    logger.info("✓ Recommendations router loaded")
except Exception as e:
    logger.error(f"✗ Recommendations router failed: {e}")

@app.get('/health')
async def health_check():
    logger.info("Health check called")
    return {
        "status": "ok",
        "message": "Backend running successfully ✅",
        "version": "1.0.0"
    }

@app.get('/')
async def root():
    return {
        "message": "AI Career Advisor API",
        "status": "running",
        "docs": "/docs"
    }

logger.info("=" * 60)
logger.info("AI Career Advisor API Started")
logger.info("=" * 60)
