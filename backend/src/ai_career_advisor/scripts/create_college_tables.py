"""
Script to create college program cache tables
Run: python -m ai_career_advisor.scripts.create_college_tables
"""
import asyncio
import sys
import os

# Add src to path if run directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ai_career_advisor.core.database import engine, Base
from ai_career_advisor.models.college_program_cache import CollegeProgramCache

async def create_tables():
    """Create college program cache table"""
    print("Creating college program cache table...")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("[OK] Table `college_program_cache` created successfully!")

if __name__ == "__main__":
    asyncio.run(create_tables())
