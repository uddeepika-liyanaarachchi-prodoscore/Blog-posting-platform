
from datetime import datetime, timedelta,timezone

import bcrypt
import jwt

from app.core.config import settings

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"),hashed_password.encode("utf-8"))

# Create the Access Token - Short Lived
def create_access_token(data:dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.JWT_ACCESS_TOKEN, algorithm=settings.JWT_ALGORITHM) 

# Create the Refresh Token - Long Lived
def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.JWT_REFRESH_TOKEN, algorithm=settings.JWT_ALGORITHM) 
    

# 3. Decode & Verify Access Token
def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_ACCESS_TOKEN, algorithms=[settings.JWT_ALGORITHM])

# 4. Decode & Verify Refresh Token
def decode_refresh_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_REFRESH_TOKEN, algorithms=[settings.JWT_ALGORITHM])