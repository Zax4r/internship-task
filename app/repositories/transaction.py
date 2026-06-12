from datetime import datetime, timezone

from sqlalchemy import select, update
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

    async def get_transaction_by_id(self, transaction_id: int) -> Transaction | None:
        query = select(Transaction).where(Transaction.id == transaction_id)
        transaction_result = await self.session.execute(query)
        transaction = transaction_result.scalar_one_or_none()
        return transaction

    async def add_transaction(self, user_id: int, currency, amount: float) -> Transaction:
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
        await self.session.execute(update(Transaction).values(status=new_status).where(Transaction.id == transaction_id))
