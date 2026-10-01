from typing import Optional

from fastapi import UploadFile

from app.core.cloudinary_util import upload_image_to_cloudinary
from app.model.posts_model import PostStatus, Posts_Model
from app.repository.interfaces.post_repo_interface import IPostRepository
from app.schemas.posts_schema import PostCreate



class PostService:
    def __init__(self, post_repository: IPostRepository):
        self._post_repository = post_repository

    async def create_post(
        self, 
        dto:PostCreate,
        user_id: int, 
        image: Optional[UploadFile] = None
    ) -> Posts_Model:
        image_url = None
        if image:
            image_url = upload_image_to_cloudinary(image)

        new_post = Posts_Model(
            title=dto.title,
            content=dto.content,
            image_url=image_url,
            status=PostStatus.PUBLISHED.value,
            user_id=user_id
        )
        return await self._post_repository.create(new_post)