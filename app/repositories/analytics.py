from datetime import date

from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import TransactionStatusEnum
from app.models.transaction import Transaction
from app.models.user import User


class AnalyticsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_registered_users_count(self, dt_gt: date, dt_lt: date) -> int:
        q = select(func.count(distinct(User.id))).where((func.date(User.created) >= dt_gt) & (func.date(User.created) <= dt_lt))
        registered_users_result = await self.session.execute(q)
        registered_users = registered_users_result.scalar_one()
        return registered_users

    async def get_deposit_users_count(self, dt_gt: date, dt_lt: date) -> int:
        q = (
            select(func.count(distinct(User.id)))
            .join(Transaction, Transaction.user_id == User.id)
            .where(
                (func.date(User.created) >= dt_gt)
                & (func.date(User.created) <= dt_lt)
                & (func.date(Transaction.created) >= dt_gt)
                & (func.date(Transaction.created) <= dt_lt)
                & (Transaction.amount > 0)
            )
        )
        users_with_transactions_result = await self.session.execute(q)
        users_with_transactions = users_with_transactions_result.scalar_one()
        return users_with_transactions

    async def get_not_rollbacked_deposits(self, dt_gt: date, dt_lt: date) -> list[Transaction]:
        q = select(Transaction).where(
            (func.date(Transaction.created) >= dt_gt)
            & (func.date(Transaction.created) <= dt_lt)
            & (Transaction.amount > 0)
            & (Transaction.status != TransactionStatusEnum.roll_backed.value)
        )
        not_rollbacked_deposits_result = await self.session.execute(q)
        not_rollbacked_deposits = not_rollbacked_deposits_result.scalars().all()
        return list(not_rollbacked_deposits)

    async def get_not_rollbacked_withdraws(self, dt_gt: date, dt_lt: date) -> list[Transaction]:
        q = select(Transaction).where(
            (func.date(Transaction.created) >= dt_gt)
            & (func.date(Transaction.created) <= dt_lt)
            & (Transaction.amount < 0)
            & (Transaction.status != TransactionStatusEnum.roll_backed.value)
        )
        not_rollbacked_withdraws_result = await self.session.execute(q)
        not_rollbacked_withdraws = not_rollbacked_withdraws_result.scalars().all()
        return list(not_rollbacked_withdraws)

    async def get_transactions_count(self, dt_gt: date, dt_lt: date) -> int:
        q = select(func.count(distinct(Transaction.id))).where(
            (func.date(Transaction.created) >= dt_gt) & (func.date(Transaction.created) <= dt_lt)
        )
        transactions_result = await self.session.execute(q)
        transactions = transactions_result.scalar_one()
        return transactions

    async def get_not_rollbacked_transactions_count(self, dt_gt: date, dt_lt: date) -> int:
        q = select(func.count(distinct(Transaction.id))).where(
            (func.date(Transaction.created) >= dt_gt)
            & (func.date(Transaction.created) <= dt_lt)
            & (Transaction.status != TransactionStatusEnum.roll_backed.value)
        )
        transactions_result = await self.session.execute(q)
        transactions = transactions_result.scalar_one()
        return transactions
