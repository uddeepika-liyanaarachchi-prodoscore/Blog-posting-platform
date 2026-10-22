from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.db import get_db_session
from app.model.user_model import UserModel
from app.core.security import create_access_token, create_refresh_token
import os

router = APIRouter(prefix="/auth", tags=["Auth"])


GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID 

class GoogleAuthRequest(BaseModel):
    token: str

@router.get("/config/google-client-id")
async def get_google_client_id():
    return {"client_id": os.getenv("GOOGLE_CLIENT_ID")}

@router.post("/google")
async def google_auth(payload: GoogleAuthRequest, db: AsyncSession = Depends(get_db_session)):
    try:
        id_info = id_token.verify_oauth2_token(
            payload.token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )

        email = id_info.get("email")
        first_name = id_info.get("given_name", "")
        last_name = id_info.get("family_name", "")

        if not email:
            raise HTTPException(status_code=400, detail="Google token does not contain email")

        stmt = select(UserModel).where(UserModel.email == email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            user = UserModel(
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_google_user=True, 
                hashed_password=None
                )
            db.add(user)
            await db.commit()
            await db.refresh(user)

        payload = {
            "sub": user.email,
            "user_id": user.id,
            "role": user.role
        } # type: ignore

        
        return {
            "success": True,
            "id": user.id,
            "access_token": payload.token,
            "message": "Google Login Successful"
        }

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Google token"
        )