from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ai_career_advisor.core.database import get_db
from ai_career_advisor.services.profile_service import ProfileService
from ai_career_advisor.Schemas.profile import (
    ProfileResponse,
    ProfileCreate,
    ProfileUpdate,
)
from ai_career_advisor.core.security import get_current_user


router = APIRouter(prefix="/profile", tags=["Profile"])

@router.get("", response_model = ProfileResponse)
async def get_my_profile(db:AsyncSession = Depends(get_db),
                         current_user  = Depends(get_current_user)):
    
    profile = await ProfileService.get_by_user_id(db, current_user.id)

    if not profile:
        raise HTTPException(status_code = 404, detail = "Profile not found")
    return profile

@router.put("", response_model = ProfileResponse)
async def update_my_profile(
    data: ProfileUpdate,
    db:AsyncSession = Depends(get_db),
    current_user  = Depends(get_current_user),
):
    profile = await ProfileService.get_by_user_id(db, current_user.id)

    if not profile:
        raise HTTPException(status_code = 404, detail = "Profile not found")

    updated = await ProfileService.update_profile(db, profile, data)
    return updated

@router.post("", response_model = ProfileResponse)

async def create_profile(
    data: ProfileCreate,
    db:AsyncSession = Depends(get_db),
    current_user  = Depends(get_current_user)
):
    existing = await ProfileService.get_by_user_id(db, current_user.id)
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists")
    
    new_profile = await ProfileService.create_profile(db, current_user.id, data)
    return new_profile
    

