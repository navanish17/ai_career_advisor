from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_career_advisor.core.database import get_db
from ai_career_advisor.core.security import hash_password , verify_password,get_current_user
from ai_career_advisor.Schemas.user import UserCreate, UserResponse, UserLogin
from ai_career_advisor.models.user import User
from ai_career_advisor.core.jwt_handler import create_access_token, decode_access_token
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


@router.post("/login")
async def login(payload :UserLogin, db:AsyncSession = Depends(get_db)):
    logger.info(f"Login trial for the user : {payload.email}")

    #search user from the database

    stmt = select(User).where(User.email==payload.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    # let suppose user not found 

    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid email or password"
        )
    
    # Verify the given password

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid email or password"
        )
    
    # now we will create token and return to the user
    #create token 
    token  = create_access_token({"user_id": user.id})

    #return user + token 

    return {
        "user": {"id": user.id,
                "name": user.name,
                "email": user.email
        },
        "access_token": token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return UserResponse.model_validate(current_user)

                 







