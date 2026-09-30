from app.schemas.user_schema import RefreshTokenRequestSchema, TokenResponseSchema, UserLoginSchema, UserRegisterSchema, UserResponseSchema
from app.service.user_service import AuthService

async def register_user(body: UserRegisterSchema, service: AuthService) -> UserResponseSchema:
    user = await service.register(body)
    return UserResponseSchema.model_validate(user)

async def login_user(body: UserLoginSchema, service: AuthService) -> TokenResponseSchema:
    user = await service.login(body)
    return TokenResponseSchema(**user)

async def refresh_user_token(body: RefreshTokenRequestSchema, service: AuthService) -> TokenResponseSchema:
    tokens = await service.refresh_access_token(body.refresh_token)
    return TokenResponseSchema(**tokens)