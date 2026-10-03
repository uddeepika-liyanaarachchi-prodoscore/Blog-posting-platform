from abc import abstractmethod
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.posts_model import PostStatus, Posts_Model
from app.model.user_model import UserModel
from app.repository.interfaces.post_repo_interface import IPostRepository

class PostRepository(IPostRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, post: Posts_Model) -> Posts_Model:
        self._session.add(post)
        await self._session.commit()
        await self._session.refresh(post)
        return post

    async def get_by_id(self, post_id: int) -> Posts_Model | None:
        result = await self._session.execute(select(Posts_Model).where(Posts_Model.id==post_id))
        return result.scalars().first()

    async def get_posts_by_user_id(self,user_id:int) -> List[Posts_Model]:
        result = await self._session.execute(
            select(Posts_Model).where(Posts_Model.user_id == user_id)
        )
        return list(result.scalars().all())

    async def update(self, post: Posts_Model) -> Posts_Model:
         self._session.add(post)
         await self._session.commit()
         await self._session.refresh(post)
         return post

    async def delete(self, post: Posts_Model) -> Posts_Model:
         self._session.add(post)
         await self._session.commit()
         await self._session.refresh(post)
         return post
    
    async def update_status(self, post: Posts_Model) -> Posts_Model:
             self._session.add(post)
             await self._session.commit()
             await self._session.refresh(post)
             return post

    async def get_all_published(self) -> List[Posts_Model]:
        stmt = (
            select(Posts_Model)
            .where(Posts_Model.status == PostStatus.PUBLISHED)
            .order_by(Posts_Model.id.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    