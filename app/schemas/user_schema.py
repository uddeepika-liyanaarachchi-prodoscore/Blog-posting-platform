
from pydantic import BaseModel, EmailStr
from app.model.user_model import Role

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

class UserResponseSchema(BaseModel):
    id: int
    email: EmailStr
    role: Role  

    class Config:
        from_attributes = True