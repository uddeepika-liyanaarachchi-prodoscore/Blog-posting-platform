from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.posts_model import Posts_Model
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
        result = await self._session.execute(select(Posts_Model).where(UserModel.id==post_id))
        return result.scalars().first()

    async def get_all_published(self) -> List[Posts_Model]:
        raise NotImplementedError

    async def update(self, post: Posts_Model) -> Posts_Model:
         self._session.add(post)
         await self._session.commit()
         await self._session.refresh(post)
         return post

    async def delete(self, post: Posts_Model) -> None:
        raise NotImplementedError

    async def update_status(self, post: Posts_Model) -> Posts_Model:
             self._session.add(post)
             await self._session.commit()
             await self._session.refresh(post)
             return post
