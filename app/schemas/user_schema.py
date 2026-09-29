
from pydantic import BaseModel, EmailStr
from app.model.user_model import Role


class UserRegisterSchema(BaseModel):
    email: EmailStr
    password: str

class UserResponseSchema(BaseModel):
    id: int
    email: EmailStr
    role: Role  

    class Config:
        from_attributes = True