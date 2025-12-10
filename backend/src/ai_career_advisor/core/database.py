from typing import AsyncGenerator
import os
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)

from sqlalchemy.orm import DeclarativeBase


# Sqlite fallback for development

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///D:/Cdac_project/project_02/dev.db"
)


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


