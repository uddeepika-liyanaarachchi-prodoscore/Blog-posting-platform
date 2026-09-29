from enum import Enum
from sqlalchemy import Column, Integer, String
from app.core.db import Base


class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"

class UserModel(Base):
    __tablename__="users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255),unique=True,nullable=False,index=True)
    hashed_password = Column(String(255),nullable=False)
    role = Column(String(50),nullable=False,default=Role.USER.value)   