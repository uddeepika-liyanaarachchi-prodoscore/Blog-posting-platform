from enum import Enum
from typing import Optional
from pydantic import BaseModel

class PostStatusEnum(str, Enum):
    PUBLISHED = "PUBLISHED"
    UNPUBLISHED = "UNPUBLISHED"

class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class PostResponse(PostBase):
    id: int
    image_url: Optional[str]
    status: PostStatusEnum
    user_id: int

    class Config:
        from_attributes = True