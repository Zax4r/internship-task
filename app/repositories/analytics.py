from datetime import date, timedelta

from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import TransactionStatusEnum
from app.models.transaction import Transaction
from app.models.user import User


class AnalyticsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_registered_users_count(self, dt_from: date, dt_to: date) -> int:
        q = select(func.count(distinct(User.id))).where(
            (User.created >= dt_from) & (User.created <= dt_to + timedelta(days=1))
        )
        registered_users_result = await self.session.execute(q)
        registered_users = registered_users_result.scalar_one()
        return registered_users

    async def get_deposit_users_count(self, dt_from: date, dt_to: date) -> int:
        q = (
            select(func.count(distinct(User.id)))
            .join(Transaction, Transaction.user_id == User.id)
            .where(
                (User.created >= dt_from)
                & (User.created <= dt_to + timedelta(days=1))
                & (Transaction.created >= dt_from)
                & (Transaction.created <= dt_to + timedelta(days=1))
                & (Transaction.amount > 0)
            )
        )
        users_with_transactions_result = await self.session.execute(q)
        users_with_transactions = users_with_transactions_result.scalar_one()
        return users_with_transactions

    async def get_not_rollbacked_deposits(self, dt_from: date, dt_to: date) -> list[Transaction]:
        q = select(Transaction).where(
            (Transaction.created >= dt_from)
            & (Transaction.created <= dt_to + timedelta(days=1))
            & (Transaction.amount > 0)
            & (Transaction.status != TransactionStatusEnum.roll_backed.value)
        )
        not_rollbacked_deposits_result = await self.session.execute(q)
        not_rollbacked_deposits = not_rollbacked_deposits_result.scalars().all()
        return list(not_rollbacked_deposits)

    async def get_not_rollbacked_withdraws(self, dt_from: date, dt_to: date) -> list[Transaction]:
        q = select(Transaction).where(
            (Transaction.created >= dt_from)
            & (Transaction.created <= dt_to + timedelta(days=1))
            & (Transaction.amount < 0)
            & (Transaction.status != TransactionStatusEnum.roll_backed.value)
        )
        not_rollbacked_withdraws_result = await self.session.execute(q)
        not_rollbacked_withdraws = not_rollbacked_withdraws_result.scalars().all()
        return list(not_rollbacked_withdraws)

    async def get_transactions_count(self, dt_from: date, dt_to: date) -> int:
        q = select(func.count(distinct(Transaction.id))).where(
            (Transaction.created >= dt_from) & (Transaction.created <= dt_to + timedelta(days=1))
        )
        transactions_result = await self.session.execute(q)
        transactions = transactions_result.scalar_one()
        return transactions

    async def get_not_rollbacked_transactions_count(self, dt_from: date, dt_to: date) -> int:
        q = select(func.count(distinct(Transaction.id))).where(
            (Transaction.created >= dt_from)
            & (Transaction.created <= dt_to + timedelta(days=1))
            & (Transaction.status != TransactionStatusEnum.roll_backed.value)
        )
        transactions_result = await self.session.execute(q)
        transactions = transactions_result.scalar_one()
        return transactions
