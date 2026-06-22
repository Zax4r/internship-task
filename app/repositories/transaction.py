from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import TransactionStatusEnum
from app.models.transaction import Transaction


class TransactionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_transactions(self, user_id: int | None) -> list[Transaction]:
        query = select(Transaction).order_by(Transaction.created.desc())
        if user_id:
            query = query.where(Transaction.user_id == user_id)

        transaction_result = await self.session.execute(query)
        transactions = transaction_result.scalars().all()
        return list(transactions)

    async def get_transaction_by_id(self, transaction_id: int) -> Transaction:
        query = select(Transaction).where(Transaction.id == transaction_id)
        transaction_result = await self.session.execute(query)
        transaction = transaction_result.scalar_one()
        return transaction

    async def add_transaction(self, user_id: int, currency: str, amount: Decimal) -> Transaction:
        new_transaction = Transaction(
            user_id=user_id,
            currency=currency,
            amount=amount,
            status=TransactionStatusEnum.processed.value,
            created=datetime.now(timezone.utc),
        )
        self.session.add(new_transaction)
        await self.session.flush()
        await self.session.refresh(new_transaction)
        return new_transaction

    async def update_transaction(self, transaction_id: int, new_status: str) -> None:
        await self.session.execute(
            update(Transaction).values(status=new_status).where(Transaction.id == transaction_id)
        )


class FakeTransactionRepository:
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
            status=TransactionStatusEnum.processed.value,
            created=datetime.now(timezone.utc),
        )
        self.transactions[self.next_transaction_id] = new_transaction
        self.next_transaction_id += 1
        return new_transaction

    async def update_transaction(self, transaction_id: int, new_status: str) -> None:
        self.transactions[transaction_id].status = new_status
