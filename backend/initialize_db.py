"""
Database Initialization Script
Creates all tables in the SQLite database.
RUN FROM: backend/ directory
COMMAND: python initialize_db.py
"""

import asyncio
import sys
import os

# CRITICAL FIX: Add backend to path FIRST so imports match the models
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BACKEND_DIR)

# Now import using the SAME path the models use (ai_career_advisor, NOT src.ai_career_advisor)
from ai_career_advisor.core.database import engine, Base

# Import ALL models so Base.metadata knows about them
# This is crucial - if we don't import them, create_all() won't know they exist
from ai_career_advisor.models.user import User
from ai_career_advisor.models.profile import Profile
from ai_career_advisor.models.roadmap import Roadmap
from ai_career_advisor.models.roadmap_step import RoadmapStep
from ai_career_advisor.models.chatconversation import ChatConversation
from ai_career_advisor.models.quiz_question import QuizQuestion
from ai_career_advisor.models.college import College
from ai_career_advisor.models.degree import Degree
from ai_career_advisor.models.branch import Branch
from ai_career_advisor.models.career import Career
from ai_career_advisor.models.exam_alert import ExamAlert

# from ai_career_advisor.models.backward_roadmap import BackwardRoadmap
# from ai_career_advisor.models.career_attributes import CareerAttributes
# Add more as needed, but User is the critical one

async def init_models():
    print(f"Connecting to: {engine.url}")
    async with engine.begin() as conn:
        print("Dropping existing tables (clean slate)...")
        await conn.run_sync(Base.metadata.drop_all)
        print("Creating all tables...")
        await conn.run_sync(Base.metadata.create_all)
    print("=" * 50)
    print("SUCCESS: Database tables created!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(init_models())
