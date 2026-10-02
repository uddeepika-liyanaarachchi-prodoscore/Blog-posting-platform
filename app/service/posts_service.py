from typing import Optional
from fastapi import UploadFile

from app.core.cloudinary_util import upload_image_to_cloudinary
from app.exceptions_handling.posts_exceptions import PostsNotFoundException
from app.model.posts_model import PostStatus, Posts_Model
from app.repository.interfaces.post_repo_interface import IPostRepository
from app.schemas.posts_schema import PostCreate, PostUpdateSchema



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

    async def update_post(self,posts_id:int,data:PostUpdateSchema,image:Optional[UploadFile]=None)-> Posts_Model:
        post = await self._post_repository.get_by_id(posts_id)

        if not post or post.status == PostStatus.DELETED: # type: ignore
            raise PostsNotFoundException(posts_id)

        for key, value in data.model_dump(exclude_unset=True).items():
                setattr(post, key, value)

        # post = Posts_Model(
        #      title=data.title,
        #      content=data.content,
        #      image_url = image,
        #      status=data.status,
        #      user_id=data.user_id
        # )
        
        return await self._post_repository.update(post)