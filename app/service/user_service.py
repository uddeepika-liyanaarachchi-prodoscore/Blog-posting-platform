
from fastapi import HTTPException, status
import jwt

from app.core.exceptions import InvalidPasswordException, UserAlreadyExistsException
from app.core.security import create_access_token, create_refresh_token, decode_refresh_token, hash_password, verify_password
from app.repository.base import IUserRepository
from app.schemas.user_schema import UserLoginSchema, UserRegisterSchema
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

    async def register_admin(self, data: UserRegisterSchema) -> UserModel:
           existing_user = await self._user_repository.get_by_email(data.email)
           if existing_user:
               raise UserAlreadyExistsException(email=data.email)
    
           hashed_pwd = hash_password(data.password)
           new_user = UserModel(
               email=data.email,
               hashed_password=hashed_pwd,
               role=Role.ADMIN.value
           )
           print(new_user)
           print(new_user.role)

           return await self._user_repository.create(new_user)

    
    async def login(self,data: UserLoginSchema) -> dict:
        user = await self._user_repository.get_by_email(data.email)

        if not user or not verify_password(data.password,str(user.hashed_password)):
            raise InvalidPasswordException()

        payload = {
            "sub": user.email,
            "user_id": user.id,
            "role": user.role
        }

        access_token = create_access_token(payload)
        refresh_token = create_refresh_token(payload)

        return{
            "access_token":access_token,
            "refresh_token": refresh_token,
            "role":user.role,
            "token_type": "bearer"
        }

    async def refresh_access_token(self,refresh_token_str:str) -> dict:
        try:
            payload=decode_refresh_token(refresh_token_str)
            if payload.get("type") != "refresh":
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Token Type")

            new_payload = {
                "sub": payload["sub"],
                "user_id": payload["user_id"],
                "role": payload["role"]
            }
            new_access_token = create_access_token(new_payload)

            return {
                "access_token": new_access_token,
                "refresh_token": refresh_token_str,
                "token_type": "bearer"
            }
    
        except jwt.PyJWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid or expired refresh token")
