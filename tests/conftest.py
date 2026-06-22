import pytest
from faker import Faker

from app.core.enums import CurrencyEnum, UserStatusEnum
from app.core.uow import FakeUnitOfWork
from app.models.user import User
from app.repositories.transaction import FakeTransactionRepository
from app.repositories.user import FakeUserRepository
from app.services.transaction import TransactionService
from app.services.user import UserService


@pytest.fixture(scope='function')
def uow() -> FakeUnitOfWork:
    return FakeUnitOfWork()


@pytest.fixture(scope='function')
def user_repo() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture(scope='function')
def transaction_repo() -> FakeTransactionRepository:
    return FakeTransactionRepository()


@pytest.fixture(scope='function')
def user_service(uow: FakeUnitOfWork, user_repo: FakeUserRepository) -> UserService:
    return UserService(uow, user_repo)


@pytest.fixture(scope='function')
def transaction_service(
    uow: FakeUnitOfWork, user_repo: FakeUserRepository, transaction_repo: FakeTransactionRepository
) -> TransactionService:
    return TransactionService(uow, user_repo, transaction_repo)


@pytest.fixture(scope='function')
async def active_user(user_repo: FakeUserRepository, faker: Faker) -> User:
    user1 = await user_repo.add_user(faker.email(safe=True))
    await user_repo.add_user_balance(user1.id, CurrencyEnum.USD.value, amount='200')
    return user1


@pytest.fixture(scope='function')
async def blocked_user(user_repo: FakeUserRepository, faker: Faker) -> User:
    user1 = await user_repo.add_user(faker.email(safe=True), UserStatusEnum.BLOCKED.value)
    return user1
