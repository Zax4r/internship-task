from abc import ABC, abstractmethod
from decimal import Decimal

from app.models.transaction import Transaction


class BaseTransactionRepository(ABC):
    @abstractmethod
    async def get_transactions(self, user_id: int | None) -> list[Transaction]: ...

    @abstractmethod
    async def get_transaction_by_id(self, transaction_id: int) -> Transaction: ...

    @abstractmethod
    async def add_transaction(self, user_id: int, currency: str, amount: Decimal) -> Transaction: ...

    @abstractmethod
    async def update_transaction(self, transaction_id: int, new_status: str) -> None: ...
