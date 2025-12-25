from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ai_career_advisor.Schemas.profile import StreamUpdateRequest
from ai_career_advisor.Schemas.profile import ClassLevelUpdateRequest



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

@router.post("/class-level")
async def update_class_level(
    payload: ClassLevelUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    updated_profile = await ProfileService.update_class_level(
        db=db,
        user_id=current_user.id,
        class_level=payload.class_level
    )

    return {
        "message": "Class level updated successfully",
        "class_level": updated_profile.class_level
    }


@router.post("/stream")
async def update_stream_for_12th_student(
    payload: StreamUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    updated_profile = await ProfileService.update_stream(
        db=db,
        user_id=current_user.id,
        stream=payload.stream
    )

    return {
        "message": "Stream updated successfully",
        "stream": updated_profile.stream
    }


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
    

