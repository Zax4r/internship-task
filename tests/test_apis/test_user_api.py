import pytest
from httpx import AsyncClient

from app.models.user import User
from main import app


@pytest.mark.asyncio
async def test_get_users(
    client: AsyncClient,
    active_user: User,
) -> None:
    url = app.url_path_for('get_users')

    response = await client.get(url)

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]['id'] == active_user.id
