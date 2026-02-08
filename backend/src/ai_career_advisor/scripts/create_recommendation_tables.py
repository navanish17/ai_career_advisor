"""
Script to create recommendation tables directly
Run: python -m ai_career_advisor.scripts.create_recommendation_tables
"""
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ai_career_advisor.core.database import engine, Base
from ai_career_advisor.models.user_preferences import UserPreferences
from ai_career_advisor.models.career_attributes import CareerAttributes
from ai_career_advisor.models.user_career_interaction import UserCareerInteraction


async def create_tables():
    """Create all recommendation tables"""
    print("Creating recommendation tables...")
    
    async with engine.begin() as conn:
        # Phase 4 schema refresh
        from sqlalchemy import text
        print("Dropping old career_attributes table for schema refresh...")
        await conn.execute(text("DROP TABLE IF EXISTS career_attributes"))
        await conn.run_sync(Base.metadata.create_all)
    
    print("Tables created successfully!")
    print("   - user_preferences")
    print("   - career_attributes") 
    print("   - user_career_interactions")


if __name__ == "__main__":
    asyncio.run(create_tables())
