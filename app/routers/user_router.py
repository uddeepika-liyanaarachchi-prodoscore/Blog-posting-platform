from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.user_repository import UserRepository
from app.service.user_service import AuthService
from app.schemas.user_schema import UserRegisterSchema, UserResponseSchema
from app.controller import user_controller
from app.core.db import get_db_session

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_auth_service(session: AsyncSession = Depends(get_db_session)) -> AuthService:
    repo = UserRepository(session)
    return AuthService(repo)

@router.post("/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def register(
    body: UserRegisterSchema, 
    service: AuthService = Depends(get_auth_service)
):
    return await user_controller.register_user(body, service)