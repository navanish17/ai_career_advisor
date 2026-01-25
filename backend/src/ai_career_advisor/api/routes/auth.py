from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_career_advisor.core.database import get_db
from ai_career_advisor.core.security import hash_password , verify_password,get_current_user
from ai_career_advisor.Schemas.user import UserCreate, UserResponse, UserLogin
from ai_career_advisor.models.user import User
from ai_career_advisor.services.profile_service import ProfileService
from ai_career_advisor.core.jwt_handler import create_access_token, decode_access_token
from ai_career_advisor.core.logger import logger




router = APIRouter()

@router.post("/signup", response_model=UserResponse)
async def signup(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email is already registered, try logging in"
        )
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(user_data.password)
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    await ProfileService.auto_create_profile_for_user(db, new_user.id)

    return new_user


@router.post("/login")
async def login(payload :UserLogin, db:AsyncSession = Depends(get_db)):
    logger.info(f"Login trial for the user : {payload.email}")


    stmt = select(User).where(User.email==payload.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none() 

    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid email or password"
        )
    

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid email or password"
        )
     
    token  = create_access_token({"user_id": user.id})
 

    profile = await ProfileService.get_by_user_id(db, user.id)

    user_obj = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
    }


    if profile and profile.location and profile.language:
        user_obj["isOnboarded"] = True
        user_obj["class_level"] = profile.class_level
        user_obj["stream"] = profile.stream
        user_obj["location"] = profile.location
        user_obj["language"] = profile.language
    else:
        user_obj["isOnboarded"] = False

    return {
        "user": user_obj,
        "access_token": token,
        "token_type": "bearer"
    }

@router.get("/me")
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Fetch profile
    profile = await ProfileService.get_by_user_id(db, current_user.id)
    
    # Base user data
    user_data = {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
    }
    
    # Check if onboarding is complete
    if profile and profile.location and profile.language:
        user_data["isOnboarded"] = True
        user_data["class_level"] = profile.class_level
        user_data["stream"] = profile.stream
        user_data["location"] = profile.location
        user_data["language"] = profile.language
    else:
        user_data["isOnboarded"] = False
    
    return user_data