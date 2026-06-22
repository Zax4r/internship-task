from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.enums import UserStatusEnum
from app.models.user import User, UserBalance


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_users(
        self, user_id: int | None = None, email: str | None = None, user_status: str | None = None
    ) -> list[User]:
        query = select(User).options(selectinload(User.user_balance)).order_by(User.created.desc())
        if user_id is not None:
            query = query.where(User.id == user_id)
        if email is not None:
            query = query.where(User.email == email)
        if user_status is not None:
            query = query.where(User.status == user_status)
        users_result = await self.session.execute(query)
        users = users_result.scalars().all()
        return list(users)

    async def get_user_by_email(self, email: str) -> User | None:
        query = select(User).options(selectinload(User.user_balance)).where(User.email == email)
        users_result = await self.session.execute(query)
        user = users_result.scalar_one_or_none()
        return user

    async def get_user_by_id(self, user_id: int) -> User:
        query = select(User).options(selectinload(User.user_balance)).where(User.id == user_id)
        users_result = await self.session.execute(query)
        user = users_result.scalar_one()
        return user

    async def get_user_balance(self, user_id: int, currency: str) -> UserBalance:
        query = select(UserBalance).where((UserBalance.user_id == user_id) & (UserBalance.currency == currency))
        balances_result = await self.session.execute(query)
        balance = balances_result.scalar_one()
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

    async def update_user_balance(self, balance_id: int, new_amount: Decimal) -> None:
        await self.session.execute(update(UserBalance).values(amount=new_amount).where(UserBalance.id == balance_id))


class FakeUserRepository:
    def __init__(self):
        self.users: dict[int, User] = {}
        self.balances: dict[int, UserBalance] = {}
        self.next_user_id = 1
        self.next_balance_id = 1

    async def get_users(
        self, user_id: int | None = None, email: str | None = None, user_status: str | None = None
    ) -> list[User]:
        result = list(self.users.values())
        if user_id is not None:
            result = [u for u in result if u.id == user_id]
        if email is not None:
            result = [u for u in result if u.email == email]
        if user_status is not None:
            result = [u for u in result if u.status == user_status]
        return result

    async def get_user_by_email(self, email: str) -> User | None:
        return next((u for u in self.users.values() if u.email == email), None)

    async def get_user_by_id(self, user_id: int) -> User:
        try:
            return self.users[user_id]
        except KeyError:
            raise NoResultFound

    async def get_user_balance(self, user_id: int, currency: str) -> UserBalance:
        try:
            return next((b for b in self.balances.values() if b.user_id == user_id and b.currency == currency))
        except StopIteration:
            raise NoResultFound

    async def add_user(self, email: str, status: str = UserStatusEnum.ACTIVE.value) -> User:
        user = User(
            id=self.next_user_id,
            email=email,
            status=status,
            created=datetime.now(timezone.utc),
            user_balance=[],
        )
        self.users[user.id] = user
        self.next_user_id += 1
        return user

    async def add_user_balance(self, user_id: int, currency: str, amount: str = '0') -> UserBalance:
        balance = UserBalance(
            id=self.next_balance_id,
            user_id=user_id,
            currency=currency,
            amount=Decimal(amount),
            created=datetime.now(timezone.utc),
        )
        self.balances[balance.id] = balance
        self.next_balance_id += 1
        return balance

    async def update_user(self, user_id: int, new_status: str) -> None:
        self.users[user_id].status = new_status

    async def update_user_balance(self, balance_id: int, new_amount: Decimal) -> None:
        self.balances[balance_id].amount = new_amount
