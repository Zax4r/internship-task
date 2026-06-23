import pytest
from httpx import ASGITransport, AsyncClient

from app.routers.transaction import get_transaction_service
from app.routers.user import get_user_service
from app.services.transaction import TransactionService
from app.services.user import UserService
from main import app


@pytest.fixture(scope='function')
async def client(user_service: UserService, transaction_service: TransactionService):

    app.dependency_overrides[get_user_service] = lambda: user_service
    app.dependency_overrides[get_transaction_service] = lambda: transaction_service

    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://') as ac:
        yield ac

    app.dependency_overrides.clear()
