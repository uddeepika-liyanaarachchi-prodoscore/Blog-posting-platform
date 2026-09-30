
from datetime import datetime, timedelta,timezone

from fastapi import BackgroundTasks, HTTPException, status
import jwt

from app.core.email import generate_otp, send_otp_email
from app.core.exceptions import InvalidPasswordException, UserAlreadyExistsException
from app.core.security import create_access_token, create_refresh_token, decode_refresh_token, hash_password, verify_password
from app.model.password_reset_model import PasswordResetModel
from app.repository.base import IUserRepository
from app.schemas.user_schema import ForgotPasswordRequestSchema, ResetPasswordRequestSchema, UserLoginSchema, UserProfileUpdateSchema, UserRegisterSchema
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
            raise InvalidPasswordException(email=data.email)

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
                "role": payload["role"],
                "token_type": "bearer"
            }
    
        except jwt.PyJWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid or expired refresh token")

    async def get_profile(self, user_id: int):
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    async def update_profile(self, user_id: int, update_data: UserProfileUpdateSchema):
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(user, key, value)

        return await self._user_repository.update(user)

    async def request_password_reset(self, data: ForgotPasswordRequestSchema, bg_tasks: BackgroundTasks):
        user = await self._user_repository.get_by_email(data.email)
        if not user:
            return {"message": "If this email exists, an OTP has been sent."}

        otp = generate_otp()
        expires = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=10)

        reset_entry = PasswordResetModel(
            email=data.email,
            otp_code=otp,
            expires_at=expires
        )
        await self._user_repository.save_otp(reset_entry)

        bg_tasks.add_task(send_otp_email, data.email, otp)
        return {"message": "If this email exists, an OTP has been sent."}

    async def reset_password(self, data: ResetPasswordRequestSchema):
        otp_record = await self._user_repository.get_valid_otp(data.email, data.otp)
        if not otp_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Invalid or expired OTP"
            )

        user = await self._user_repository.get_by_email(data.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Update Password & Mark OTP as used
        user.hashed_password = hash_password(data.new_password)  # type: ignore
        otp_record.is_used = True  # type: ignore
        await self._user_repository.update(user)
        await self._user_repository.save_otp(otp_record) 
        return {"message": "Password reset successfully. You can now login with your new password."}