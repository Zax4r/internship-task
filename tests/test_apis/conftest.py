import pytest
from httpx import ASGITransport, AsyncClient

from app.routers.user import get_user_service
from app.services.user import UserService
from main import app


@pytest.fixture(scope='function')
async def client(user_service: UserService):

    app.dependency_overrides[get_user_service] = lambda: user_service

    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://') as ac:
        yield ac

    app.dependency_overrides.clear()
