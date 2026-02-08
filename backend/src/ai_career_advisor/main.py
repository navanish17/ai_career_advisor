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
