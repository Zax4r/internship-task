import pytest

from app.core.uow import FakeUnitOfWork
from app.repositories.user import FakeUserRepository
from app.services.user import UserService


@pytest.fixture(scope='function')
def uow():
    return FakeUnitOfWork()


@pytest.fixture(scope='function')
def user_repo():
    return FakeUserRepository()


@pytest.fixture(scope='function')
def user_service(uow, user_repo):
    return UserService(uow, user_repo)
