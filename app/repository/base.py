from abc import ABC, abstractmethod
from typing import Optional

from app.model.user_model import UserModel

class IUserRepository(ABC):
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[UserModel]:
        pass

    @abstractmethod
    async def create(self, entity: UserModel) -> UserModel:
        pass