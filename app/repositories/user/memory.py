from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.exc import NoResultFound

from app.core.enums import UserStatusEnum
from app.models.user import User, UserBalance
from app.repositories.user.base import BaseUserRepository


class FakeUserRepository(BaseUserRepository):
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
