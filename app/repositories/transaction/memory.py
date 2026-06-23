from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.exc import NoResultFound

from app.core.enums import TransactionStatusEnum
from app.models.transaction import Transaction
from app.repositories.transaction.base import BaseTransactionRepository


class FakeTransactionRepository(BaseTransactionRepository):
    def __init__(self):
        self.transactions: dict[int, Transaction] = {}
        self.next_transaction_id = 1

    async def get_transactions(self, user_id: int | None) -> list[Transaction]:
        transactions = list(self.transactions.values())
        if user_id:
            transactions = [t for t in transactions if t.user_id == user_id]
        return transactions

    async def get_transaction_by_id(self, transaction_id: int) -> Transaction:
        try:
            return self.transactions[transaction_id]
        except KeyError:
            raise NoResultFound

    async def add_transaction(self, user_id: int, currency: str, amount: Decimal) -> Transaction:
        new_transaction = Transaction(
            id=self.next_transaction_id,
            user_id=user_id,
            currency=currency,
            amount=amount,
            status=TransactionStatusEnum.PROCESSED.value,
            created=datetime.now(timezone.utc),
        )
        self.transactions[self.next_transaction_id] = new_transaction
        self.next_transaction_id += 1
        return new_transaction

    async def update_transaction(self, transaction_id: int, new_status: str) -> None:
        self.transactions[transaction_id].status = new_status
