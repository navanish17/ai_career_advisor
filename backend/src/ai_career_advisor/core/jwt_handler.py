from datetime import datetime, timedelta
from jose import jwt, JWTError
from ai_career_advisor.core.config import settings

SECRET_KEY = settings.JWT_SECRET
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60*24 

def create_access_token(data:dict):

    """create jwt access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM )


def decode_access_token(token:str):
    """DEcode and verify the jwt token"""

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        return payload
    except JWTError:
        return None