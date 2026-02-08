"""
Migration script to add share_token column to roadmap table
Run: python -m ai_career_advisor.scripts.add_share_token
"""
import asyncio
from sqlalchemy import text
from ai_career_advisor.core.database import get_db, engine
from ai_career_advisor.core.logger import logger

async def add_share_token():
    print("Adding share_token column to roadmap table...")
    
    try:
        async with engine.begin() as conn:
            # Check if column exists
            result = await conn.execute(text("PRAGMA table_info(roadmap)"))
            columns = result.fetchall()
            column_names = [col[1] for col in columns]
            
            if "share_token" in column_names:
                print("share_token column already exists")
                return

            # Add column
            print("Altering table...")
            await conn.execute(text("ALTER TABLE roadmap ADD COLUMN share_token VARCHAR"))
            await conn.execute(text("CREATE UNIQUE INDEX ix_roadmap_share_token ON roadmap (share_token)"))
            
            print("Successfully added share_token column")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(add_share_token())
