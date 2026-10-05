from typing import List, Optional
import fastapi
import logging

from httpx import delete
from app.core.cloudinary_util import upload_image_to_cloudinary
from app.exceptions_handling.exceptions import PostAccessDeniedException, PostAlreadyDeletedException, PostsNotFoundException
from app.model.posts_model import PostStatus, Posts_Model
from app.repository.interfaces.post_repo_interface import IPostRepository
from app.schemas.posts_schema import PostCreate, PostUpdateSchema

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostService:
    def __init__(self, post_repository: IPostRepository):
        self._post_repository = post_repository

    async def create_post(
        self, 
        dto:PostCreate,
        user_id: int, 
        image: Optional[fastapi.UploadFile] = None
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

    async def update_post(self,posts_id:int,data:PostUpdateSchema,image:Optional[fastapi.UploadFile]=None)-> Posts_Model:
        post = await self._post_repository.get_by_id(posts_id)

        if not post:
            raise PostsNotFoundException(posts_id)

        if post.user_id != data.user_id:  # type: ignore
            raise PostAccessDeniedException()

        if post.status == PostStatus.DELETED: # type: ignore
            raise PostAlreadyDeletedException(posts_id)

        if data.title:
            post.title = data.title # type: ignore
        if data.content:
            post.content = data.content # type: ignore
            
        if post.status == PostStatus.UNPUBLISHED: # type: ignore
            return await self._post_repository.update(post)
        else:
            raise PostsNotFoundException(posts_id)

    async def unpublish_post(self,posts_id:int)->Posts_Model:
        post = await self._post_repository.get_by_id(posts_id)

        if not post:
            raise PostsNotFoundException(posts_id)

        if post.status == PostStatus.DELETED: # type: ignore
            raise PostAlreadyDeletedException(posts_id)
        
        if post.status == PostStatus.PUBLISHED: # type: ignore
            post.status = PostStatus.UNPUBLISHED # type: ignore
            return await self._post_repository.update(post)
        elif post.status == PostStatus.UNPUBLISHED:  # type: ignore
            post.status = PostStatus.PUBLISHED # type: ignore
            return await self._post_repository.update_status(post)
        else:
            raise PostsNotFoundException(posts_id)

    async def delete_post(self,posts_id:int)->Posts_Model:
        post = await self._post_repository.get_by_id(posts_id)

        if not post:
            raise PostsNotFoundException(posts_id)

        if post.status == PostStatus.DELETED: # type: ignore
            raise PostAlreadyDeletedException(posts_id)
        
        if post.status == PostStatus.UNPUBLISHED: # type: ignore
            post.status = PostStatus.DELETED # type: ignore
            return await self._post_repository.delete(post)
        else:
            raise PostsNotFoundException(posts_id)

    async def get_posts(self,user_id:int,query: Optional[str] = None, limit: int = 10, offset: int = 0)->List[Posts_Model]:
        return await self._post_repository.get_posts_by_user_id(user_id,query=query,limit=limit,offset=offset)

    async def get_all_posts(self,query: Optional[str] = None, limit: int = 10, offset: int = 0)->List[Posts_Model]:
        return await self._post_repository.get_all_published(
            query=query,limit=limit,offset=offset
        )

