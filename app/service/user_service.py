from app.core.exceptions import UserAlreadyExistsException
from app.core.security import hash_password
from app.repository.base import IUserRepository
from app.schemas.user_schema import UserRegisterSchema
from app.model.user_model import Role, UserModel


class AuthService:
    def __init__(self, user_repo: IUserRepository):
        self._user_repository = user_repo

    async def register(self, data: UserRegisterSchema) -> UserModel:

       existing_user = await self._user_repository.get_by_email(data.email)
       if existing_user:
           raise UserAlreadyExistsException(email=data.email)

       hashed_pwd = hash_password(data.password)
       new_user = UserModel(
           email=data.email,
           hashed_password=hashed_pwd,
           role=Role.USER.value
       )
       return await self._user_repository.create(new_user)