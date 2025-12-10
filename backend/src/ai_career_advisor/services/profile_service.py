from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select 
from typing import Optional
from ai_career_advisor.models.profile import Profile
from ai_career_advisor.schemas.profile import (
    ProfileCreate,
    ProfileUpdate,
)

class ProfileService:
    @staticmethod
    

