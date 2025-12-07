from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.ext.asyncio import AsyncSession
from ai_career_advisor.core.jwt_handler import create_access_token, decode_access_token
from ai_career_advisor.core.database import get_db
from ai_career_advisor.models.user import User
from sqlalchemy import select

pwd_context = CryptContext(schemes = ["bcrypt"], deprecated = "auto")


def hash_password(password:str)-> str:
    """Hash the user password here"""
    return pwd_context.hash(password)

def verify_password(plain_password:str, hashed_password:str)-> bool:
    """This will verify the user password from the database"""
    return pwd_context.verify(plain_password, hashed_password)


bearer_scheme = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    # Extract raw token string
    token = credentials.credentials  

    # Decode JWT
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # Fetch user from DB
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user
