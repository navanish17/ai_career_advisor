from fastapi import FastAPI
from ai_career_advisor.core.logger import logger
from ai_career_advisor.core.config import settings
from ai_career_advisor.core.middleware import add_middlewares
from ai_career_advisor.services.scheduler import scheduler
from contextlib import asynccontextmanager
import ai_career_advisor.models


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting...")
    scheduler.start()
    logger.success("Scheduler started")
    
    yield
    
    logger.info("Application shutting down...")
    scheduler.stop()
    logger.info("Scheduler stopped")


def create_app() -> FastAPI:
    logger.info("Creating FastAPI application...")

    app = FastAPI(
        title=settings.PROJECT_NAME,
        debug=settings.DEBUG,
        version="1.0.0",
        lifespan=lifespan
    )

    add_middlewares(app)

    logger.info("FastAPI application created successfully.")

    return app
