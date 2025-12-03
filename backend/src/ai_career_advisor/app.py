from fastapi import FastAPI
from ai_career_advisor.core.logger import logger
from ai_career_advisor.core.config import settings

def create_app() -> FastAPI:
    """
    Application factory — responsible for creating the FastAPI app
    with all settings, middleware, routers, and startup events.
    """
    logger.info("Creating FastAPI application...")

    app = FastAPI(
        title=settings.PROJECT_NAME,
        debug=settings.DEBUG,
        version="1.0.0"
    )

    # Placeholder: routers will be added here later
    # app.include_router(...)

    # Placeholder: middleware will be added here later
    # app.middleware("http")( ... )

    logger.info("FastAPI application created successfully.")

    return app
