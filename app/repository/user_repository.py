from sqlalchemy.future import select

from app.model.user_model import UserModel
from app.repository.base import IUserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional


class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_email(self, email: str) -> Optional[UserModel]:
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        return result.scalars().first()

    async def create(self, user: UserModel) -> UserModel:
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return user
        
