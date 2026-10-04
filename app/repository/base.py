from abc import ABC, abstractmethod
from typing import Optional

from app.model.password_reset_model import PasswordResetModel
from app.model.user_model import UserModel

class IUserRepository(ABC):
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[UserModel]:
        pass

    @abstractmethod
    async def create(self, entity: UserModel) -> UserModel:
        pass

    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[UserModel]:
        pass

    @abstractmethod
    async def update(self, user: UserModel) -> UserModel:
        pass

    @abstractmethod
    async def save_otp(self, reset_entry: PasswordResetModel) -> PasswordResetModel:
        pass

    @abstractmethod
    async def get_valid_otp(self, email: str, otp: str) -> Optional[PasswordResetModel]:
        pass