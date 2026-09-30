from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.middleware.roles import authorize_roles
from app.model.user_model import Role
from app.repository.user_repository import UserRepository
from app.service.user_service import AuthService
from app.schemas.user_schema import TokenResponseSchema, UserLoginSchema, UserRegisterSchema, UserResponseSchema
from app.controller import user_controller
from app.core.db import get_db_session

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_auth_service(session: AsyncSession = Depends(get_db_session)) -> AuthService:
    repo = UserRepository(session)
    return AuthService(repo)

@router.post("/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def register(body: UserRegisterSchema,service: AuthService = Depends(get_auth_service)):
    return await user_controller.register_user(body, service)

@router.post("/register-admin", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def register_admin(body: UserRegisterSchema,service: AuthService = Depends(get_auth_service),current_user: dict = Depends(authorize_roles([Role.ADMIN])),):
    return await user_controller.create_admin_user(body, service)

@router.post("/login", response_model=TokenResponseSchema, status_code=status.HTTP_201_CREATED)
async def login(body: UserLoginSchema, service:AuthService=Depends(get_auth_service)):
    return await user_controller.login_user(body,service)


# -----------------------TEST------------------------------------------------------


@router.get("/user/profile")
async def user_profile(current_user: dict = Depends(authorize_roles([Role.USER]))):
    return {
        "message": "Welcome User! Only USER can access this.",
        "user_data": current_user
    }

@router.get("/admin/dashboard")
async def admin_dashboard(current_user: dict = Depends(authorize_roles([Role.ADMIN]))):
    return {
        "message": "Welcome Admin! High privilege area.",
        "admin_data": current_user
    }

@router.get("/me")
async def get_me(current_user: dict = Depends(authorize_roles([Role.USER, Role.ADMIN]))):
    return {
        "message": "This is accessible to both USER and ADMIN",
        "user": current_user
    }