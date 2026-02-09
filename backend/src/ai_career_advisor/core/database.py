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

from sqlalchemy.engine.url import make_url

# Reliable Logic to fix driver
try:
    if DATABASE_URL:
        # Parse the URL object from SQLAlchemy
        url_obj = make_url(DATABASE_URL)
        
        # If it's postgres or postgresql without a driver, force asyncpg
        if url_obj.drivername in ['postgres', 'postgresql']:
            url_obj = url_obj.set(drivername='postgresql+asyncpg')
            DATABASE_URL = str(url_obj)
            logger.info(f"🔧 Automatically updated DB driver to: {url_obj.drivername}")
            
except Exception as e:
    logger.error(f"Failed to parse/update DB URL: {e}")


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


