from abc import ABC, abstractmethod
from typing import List, Optional

from app.model.posts_model import Posts_Model

class IPostRepository(ABC):

    @abstractmethod
    async def create(self, post: Posts_Model) -> Posts_Model:
        pass

    @abstractmethod
    async def get_by_id(self, post_id: int) -> Optional[Posts_Model]:
        pass

    @abstractmethod
    async def get_all_published(self) -> List[Posts_Model]:
        pass

    @abstractmethod
    async def update(self, post: Posts_Model) -> Posts_Model:
        pass

    @abstractmethod
    async def delete(self, post: Posts_Model) -> Posts_Model:
        pass

    @abstractmethod
    async def update_status(self, post: Posts_Model) -> Posts_Model:
        pass

    @abstractmethod
    async def get_posts_by_user_id(self, user_id: int) -> List[Posts_Model]:
        pass