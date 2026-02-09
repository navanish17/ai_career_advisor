from typing import AsyncGenerator

import os
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)

from sqlalchemy.orm import DeclarativeBase


import logging

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sqlite fallback for development (Relative path for Linux compatibility)
DEFAULT_DB_URL = "sqlite+aiosqlite:///./dev.db"

DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)

# Log the database URL being used (masked for security)
if DATABASE_URL:
    masked_url = DATABASE_URL
    if "@" in masked_url:
        # Simple mask: keep protocol, mask credentials
        protocol = masked_url.split("://")[0]
        masked_url = f"{protocol}://****@..."
    logger.info(f"🔌 Connecting to Database: {masked_url}")
else:
    logger.warning("⚠️ No DATABASE_URL found, utilizing default")

# Fix for Neon/Render which provide postgres:// but sqlalchemy needs postgresql+asyncpg://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)


# Base class for all orm model

class Base(DeclarativeBase):
    pass

#Async Database engine

engine = create_async_engine(
    DATABASE_URL,
    echo = False,
    future = True
)

#Session Factory 
AsyncSessionLocal = async_sessionmaker(
    bind = engine,
    expire_on_commit = False,
    class_ = AsyncSession
)

#FastAPI Dependency 

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


