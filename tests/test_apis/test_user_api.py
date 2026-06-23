import pytest
from faker import Faker
from httpx import AsyncClient

from app.core.enums import UserStatusEnum
from app.models.user import User
from app.repositories.user.memory import FakeUserRepository
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


@pytest.mark.asyncio
async def test_post_users(
    client: AsyncClient,
    user_repo: FakeUserRepository,
    faker: Faker,
) -> None:
    email_str = faker.email(safe=True)
    url = app.url_path_for('post_user')

    response = await client.post(
        url,
        json={'email': email_str},
    )

    assert response.status_code == 201
    assert await user_repo.get_user_by_email(email_str)

    data = response.json()

    assert await user_repo.get_user_by_id(data['id'])


@pytest.mark.asyncio
async def test_patch_user(
    client: AsyncClient,
    user_repo: FakeUserRepository,
    active_user: User,
) -> None:
    url = app.url_path_for('patch_user', user_id=active_user.id)

    response = await client.patch(
        url,
        json={'status': UserStatusEnum.BLOCKED.value},
    )

    assert response.status_code == 200

    user_db = await user_repo.get_user_by_id(active_user.id)

    assert user_db.status == UserStatusEnum.BLOCKED.value
