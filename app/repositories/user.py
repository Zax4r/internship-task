from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.enums import UserStatusEnum
from app.models.user import User, UserBalance


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_users(self, user_id: int | None = None, email: str | None = None, user_status: str | None = None) -> list[User]:
        query = select(User).options(selectinload(User.user_balance)).order_by(User.created.desc())
        if user_id is not None:
            query = query.where(User.id == user_id)
        if email is not None:
            query = query.where(User.email == email)
        if user_status is not None:
            query = query.where(User.status == user_status)
        users_result = await self.session.execute(query)
        users = users_result.scalars().all()
        return users

    async def get_user_by_email(self, email: str) -> User | None:
        query = select(User).options(selectinload(User.user_balance)).where(User.email == email)
        users_result = await self.session.execute(query)
        user = users_result.scalar_one_or_none()
        return user

    async def get_user_by_id(self, user_id: int) -> User | None:
        query = select(User).options(selectinload(User.user_balance)).where(User.id == user_id)
        users_result = await self.session.execute(query)
        user = users_result.scalar_one_or_none()
        return user

    async def get_user_balance(self, user_id: int, currency: str) -> UserBalance:
        query = select(UserBalance).where((UserBalance.user_id == user_id) & (UserBalance.currency == currency))
        balances_result = await self.session.execute(query)
        balance = balances_result.scalar_one_or_none()
        return balance

    async def add_user(self, email: str) -> User:
        new_user = User(email=email, status=UserStatusEnum.ACTIVE.value, created=datetime.now(timezone.utc))
        self.session.add(new_user)
        await self.session.flush()
        await self.session.refresh(new_user)
        return new_user

    async def add_user_balance(self, user_id, currency: str) -> UserBalance:
        user_balance = UserBalance(user_id=user_id, currency=currency, amount=0, created=datetime.now(timezone.utc))
        self.session.add(user_balance)
        await self.session.flush()
        await self.session.refresh(user_balance)
        return user_balance

    async def update_user(self, user_id: int, new_status: str) -> None:
        await self.session.execute(update(User).values(status=new_status).where(User.id == user_id))

    async def update_user_balance(self, balance_id: int, new_amount: float) -> None:
        await self.session.execute(update(UserBalance).values(amount=new_amount).where(UserBalance.id == balance_id))
