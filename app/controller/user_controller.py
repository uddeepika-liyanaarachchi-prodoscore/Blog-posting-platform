from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.middleware.roles import authorize_roles
from app.model.user_model import Role
from app.repository.user_repository import UserRepository
from app.service.user_service import AuthService
from app.schemas.user_schema import ForgotPasswordRequestSchema, ResetPasswordRequestSchema, TokenResponseSchema, UserLoginSchema, UserProfileUpdateSchema, UserRegisterSchema, UserResponseSchema , RefreshTokenRequestSchema
from app.core.db import get_db_session

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_auth_service(session: AsyncSession = Depends(get_db_session)) -> AuthService:
    repo = UserRepository(session)
    return AuthService(repo)

@router.post("/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def register(body: UserRegisterSchema,service:AuthService=Depends(get_auth_service)):
    user = await service.register(body)
    return UserResponseSchema.model_validate(user)

@router.post("/register-admin", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def register_admin(body: UserRegisterSchema,service: AuthService = Depends(get_auth_service),current_user: dict = Depends(authorize_roles([Role.ADMIN])),):
    user = await service.register_admin(body)
    return UserResponseSchema.model_validate(user)

@router.post("/login", response_model=TokenResponseSchema, status_code=status.HTTP_200_OK)
async def login(body: UserLoginSchema, service:AuthService=Depends(get_auth_service)):
    user = await service.login(body)
    return TokenResponseSchema(**user)

@router.post("/refresh", response_model=TokenResponseSchema, status_code=status.HTTP_200_OK)
async def refresh_token(
    body: RefreshTokenRequestSchema, 
    service: AuthService = Depends(get_auth_service)
):
    tokens = await service.refresh_access_token(body.refresh_token)
    return TokenResponseSchema(**tokens)

@router.get("/profile", response_model=UserResponseSchema)
async def get_my_profile(
    current_user: dict = Depends(authorize_roles([Role.USER, Role.ADMIN])),
    service: AuthService = Depends(get_auth_service)
):
    return await service.get_profile(current_user["user_id"])

@router.put("/profile", response_model=UserResponseSchema)
async def update_my_profile(
    body: UserProfileUpdateSchema,
    current_user: dict = Depends(authorize_roles([Role.USER, Role.ADMIN])),
    service: AuthService = Depends(get_auth_service)
):
    return await service.update_profile(current_user["user_id"], body)

@router.post("/forgot-password")
async def forgot_password(
    body: ForgotPasswordRequestSchema,
    bg_tasks: BackgroundTasks,
    service: AuthService = Depends(get_auth_service)
):
    return await service.request_password_reset(body, bg_tasks)

@router.post("/reset-password")
async def reset_password(
    body: ResetPasswordRequestSchema,
    service: AuthService = Depends(get_auth_service)
):
    return await service.reset_password(body)