from enum import Enum
from typing import Optional
from pydantic import BaseModel
from pydantic import ConfigDict

class PostStatusEnum(str, Enum):
    PUBLISHED = "PUBLISHED"
    UNPUBLISHED = "UNPUBLISHED"
    DELETED = "DELETED"

class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    pass

class PostUpdateSchema(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None
    status: Optional[PostStatusEnum] = None
    user_id:Optional[int]=None

class PostResponse(PostBase):
    id: int
    image_url: Optional[str]
    status: PostStatusEnum
    user_id: int

    model_config = ConfigDict(from_attributes=True)