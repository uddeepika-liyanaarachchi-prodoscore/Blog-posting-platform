import enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.core.db import Base

class PostStatus(str, enum.Enum):
    PUBLISHED = "PUBLISHED"
    UNPUBLISHED = "UNPUBLISHED"

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=True)
    status = Column(Enum(PostStatus), default=PostStatus.PUBLISHED, nullable=False)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationship with User model
    owner = relationship("User", back_populates="posts")