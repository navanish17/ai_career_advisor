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

# Use absolute path for dev.db relative to this file to avoid CWD confusion
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent # Points to backend/
DB_PATH = BASE_DIR / "dev.db"
DEFAULT_DB_URL = f"sqlite+aiosqlite:///{DB_PATH}"

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

# Handle PostgreSQL URL for asyncpg compatibility
from urllib.parse import urlparse, urlunparse

if DATABASE_URL and DATABASE_URL.startswith(("postgres://", "postgresql://")):
    # Parse URL to strip ALL query parameters (asyncpg doesn't understand them)
    parsed = urlparse(DATABASE_URL)
    require_ssl = "sslmode=require" in (parsed.query or "")
    
    # Rebuild URL without query params and with correct driver
    clean_url = urlunparse((
        "postgresql+asyncpg",  # scheme - always use asyncpg
        parsed.netloc,         # user:pass@host:port
        parsed.path,           # /database_name
        "",                    # params
        "",                    # query - STRIPPED (asyncpg can't handle these)
        ""                     # fragment
    ))
    DATABASE_URL = clean_url

    logger.info(f"🔧 Using Database URL: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else '...' }")
else:
    require_ssl = False

# Base class for all orm model
class Base(DeclarativeBase):
    pass

# Build engine kwargs
import ssl as ssl_module
engine_kwargs = {
    "echo": False,
    "future": True,
    "pool_pre_ping": True,
}
if require_ssl:
    ssl_ctx = ssl_module.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl_module.CERT_NONE
    engine_kwargs["connect_args"] = {"ssl": ssl_ctx}

#Async Database engine
engine = create_async_engine(DATABASE_URL, **engine_kwargs)

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


