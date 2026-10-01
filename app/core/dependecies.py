# app/core/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt

from app.core.db import AsyncSessionLocal, get_db_session
from app.core.exceptions import InvalidPasswordException
from app.core.security import decode_access_token
from app.model.user_model import UserModel
from app.repository.posts_repository import PostRepository
from app.service.posts_service import PostService 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db_session)
) -> UserModel:

    
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise InvalidPasswordException("Invalid token or session expired")
            
    except jwt.PyJWTError:
        raise InvalidPasswordException("JWT Invalid token or session expired")

    user = db.query(UserModel).filter(UserModel.id == int(user_id)).first()
    if user is None:
        raise InvalidPasswordException("Invalid User")
        
    return user