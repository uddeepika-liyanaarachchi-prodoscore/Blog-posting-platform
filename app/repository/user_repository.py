from datetime import datetime, timezone
from sqlalchemy.future import select
from sqlalchemy import and_
from app.model.password_reset_model import PasswordResetModel
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
        
    async def get_by_id(self, user_id: int) -> Optional[UserModel]:
        result = await self._session.execute(select(UserModel).where(UserModel.id == user_id))
        return result.scalars().first()


    async def update(self, user: UserModel) -> UserModel:
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return user

    async def save_otp(self, reset_entry: PasswordResetModel) -> PasswordResetModel:
        self._session.add(reset_entry)
        await self._session.commit()
        return reset_entry

    async def get_valid_otp(self, email: str, otp: str) -> Optional[PasswordResetModel]:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        result = await self._session.execute(
            select(PasswordResetModel).where(
                and_(
                    PasswordResetModel.email == email,
                    PasswordResetModel.otp_code == otp,
                    PasswordResetModel.is_used == False,
                    PasswordResetModel.expires_at >= now
                )
            )
        )
        return result.scalars().first()