from app.schemas.user_schema import UserRegisterSchema, UserResponseSchema
from app.service.user_service import AuthService

async def register_user(body: UserRegisterSchema, service: AuthService) -> UserResponseSchema:
    user = await service.register(body)
    return UserResponseSchema.model_validate(user)