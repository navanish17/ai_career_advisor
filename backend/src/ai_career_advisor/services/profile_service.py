from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from ai_career_advisor.models.profile import Profile
from ai_career_advisor.Schemas.profile import (
    ProfileCreate,
    ProfileUpdate,
)

class ProfileService:
    @staticmethod
    async def get_by_user_id(db:AsyncSession, user_id : int)-> Optional[Profile]:
        result = await db.execute(select(Profile).where (Profile.user_id==user_id))

        return result.scalars().first()
    
    @staticmethod
    async def create_profile(db:AsyncSession, user_id:int, data: ProfileCreate)->Profile:
        """To create a new profile and save it in db"""
        profile = Profile(
            user_id = user_id,
            class_level = data.class_level,
            location = data.location,
            language = data.language,
            known_interests = data.known_interests

        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
        return profile
    
    @staticmethod
    async def update_profile(db:AsyncSession, profile: Profile, data: ProfileUpdate)-> Profile:
        try:
            if data.class_level is not None:
                profile.class_level = data.class_level

            if data.location is not None:
                profile.location = data.location

            if data.language is not None:
                profile.language = data.language

            if data.known_interests is not None:
                profile.known_interests = data.known_interests

            await db.commit()
            await db.refresh(profile)
            return profile
        
        except Exception:
            await db.rollback()
            raise

    @staticmethod
    async def update_class_level(
        *,
        db: AsyncSession,
        user_id: int,
        class_level: str
    ) -> Profile:

        if class_level not in ["10th", "12th"]:
            raise ValueError("Invalid class level")

        result = await db.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        profile = result.scalars().first()

        if not profile:
            raise Exception("Profile not found")

        profile.class_level = class_level
        await db.commit()
        await db.refresh(profile)

        return profile



    @staticmethod
    async def update_stream(
        *,
        db: AsyncSession,
        user_id: int,
        stream: str
    ) -> Profile:

        result = await db.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        profile = result.scalars().first()

        if not profile:
            raise Exception("Profile not found")

        profile.stream = stream
        await db.commit()
        await db.refresh(profile)

        return profile
    

    @staticmethod
    async def auto_create_profile_for_user(db:AsyncSession, user_id:int)-> Profile:
        """ Auto create profile for the user"""

        existing = await ProfileService.get_by_user_id(db, user_id)
        if existing:
            return existing
        
        empty_profile = Profile(
            user_id = user_id,
            class_level = None,
            location = None,
            language = None,
            known_interests = None
        )

        db.add(empty_profile)
        await db.commit()
        await db.refresh(empty_profile)
        return empty_profile
            



    
