from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_career_advisor.core.database import get_db
from ai_career_advisor.core.security import hash_password , verify_password, create_access_token
from ai_career_advisor.Schemas.user import UserCreate, UserResponse, UserLogin
from ai_career_advisor.models.user import User

from ai_career_advisor.core.logger import logger


router = APIRouter()

@router.post("/signup", response_model = UserResponse)
async def signup(user_data: UserCreate, db : AsyncSession = Depends(get_db)):
    #check if email exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code = 400, detail = "Email is already registered, Try to log in")
    

    #create user
    new_user = User(
        name = user_data.name,
        email = user_data.email,
        password_hash = hash_password(user_data.password)
    )
    
    #add new user to database

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user 


