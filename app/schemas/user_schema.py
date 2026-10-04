
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.model.user_model import Role
from pydantic import ConfigDict

class UserRegisterSchema(BaseModel):
    email: EmailStr
    password: str

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

class TokenResponseSchema(BaseModel):
    access_token: str
    refresh_token: str
    role:Role
    token_type: str = "bearer"

class RefreshTokenRequestSchema(BaseModel):
    refresh_token: str

class UserProfileUpdateSchema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None

class ForgotPasswordRequestSchema(BaseModel):
    email: EmailStr

class ResetPasswordRequestSchema(BaseModel):
    email: EmailStr
    otp: str
    new_password: str

class UserResponseSchema(BaseModel):
    id: int
    email: EmailStr
    role: Role  
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)