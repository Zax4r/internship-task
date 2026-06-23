from abc import ABC, abstractmethod
from decimal import Decimal

from app.models.user import User, UserBalance


class BaseUserRepository(ABC):
    @abstractmethod
    async def get_users(
        self, user_id: int | None = None, email: str | None = None, user_status: str | None = None
    ) -> list[User]: ...

    @abstractmethod
    async def get_user_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> User: ...

    @abstractmethod
    async def get_user_balance(self, user_id: int, currency: str) -> UserBalance: ...

    @abstractmethod
    async def add_user(self, email: str) -> User: ...

    @abstractmethod
    async def add_user_balance(self, user_id, currency: str) -> UserBalance: ...

    @abstractmethod
    async def update_user(self, user_id: int, new_status: str) -> None: ...

    @abstractmethod
    async def update_user_balance(self, balance_id: int, new_amount: Decimal) -> None: ...
