from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt
from sqlalchemy import select
from app.core.db import  get_db_session
from app.core.security import decode_access_token
from app.exceptions_handling.exceptions import InvalidCredentialsException
from app.model.user_model import UserModel
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db_session)
) -> UserModel:

    
    try:
        payload = decode_access_token(token)
        user_id = payload.get("user_id")
        
        if user_id is None:
            raise InvalidCredentialsException("Invalid token or session expired")
            
    except jwt.PyJWTError:
        raise InvalidCredentialsException("JWT Invalid token or session expired")

    stmt = select(UserModel).where(UserModel.id == int(user_id))
    result = await db.execute(stmt) # type: ignore
    user = result.scalar_one_or_none()
    if user is None:
        raise InvalidCredentialsException("Invalid User")
        
    return user