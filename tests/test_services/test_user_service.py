import pytest
from faker import Faker

from app.core.enums import CurrencyEnum, UserStatusEnum
from app.core.exceptions import UserAlreadyActiveException, UserAlreadyExistsException
from app.repositories.user import FakeUserRepository
from app.schemas.user import RequestListUserModel, RequestUserModel, RequestUserUpdateModel
from app.services.user import UserService


@pytest.mark.asyncio
async def test_get_users_service(user_service: UserService, user_repo: FakeUserRepository, faker: Faker) -> None:
    email_str1 = faker.email(safe=True)
    user = await user_repo.add_user(email_str1)

    users = await user_service.get_users(RequestListUserModel())

    assert len(users) == 1
    assert any(x.id == user.id for x in users)


@pytest.mark.asyncio
async def test_get_users_filter_service(user_service: UserService, user_repo: FakeUserRepository, faker: Faker) -> None:
    email_str1 = faker.email(safe=True)
    email_str2 = faker.email(safe=True)
    user1 = await user_repo.add_user(email_str1)
    user2 = await user_repo.add_user(email_str2)

    users = await user_service.get_users(
        RequestListUserModel(
            email=email_str1,
        )
    )

    assert any(x.id == user1.id for x in users)
    assert not any(x.id == user2.id for x in users)


@pytest.mark.asyncio
async def test_add_user_service(user_service: UserService, user_repo: FakeUserRepository, faker: Faker) -> None:
    email_str = faker.email(safe=True)

    user_model = await user_service.add_user(
        RequestUserModel(
            email=email_str,
        )
    )
    user_db = await user_repo.get_user_by_email(email_str)

    assert user_model.id == user_db.id
    for currency in CurrencyEnum:
        balance = await user_repo.get_user_balance(user_model.id, currency)
        assert balance.amount == 0


@pytest.mark.asyncio
async def test_add_user_service_fails(user_service: UserService, user_repo: FakeUserRepository, faker: Faker) -> None:
    email_str = faker.email(safe=True)
    await user_repo.add_user(email_str)

    with pytest.raises(UserAlreadyExistsException):
        await user_service.add_user(
            RequestUserModel(
                email=email_str,
            )
        )


@pytest.mark.asyncio
async def test_update_user_service(user_service: UserService, user_repo: FakeUserRepository, faker: Faker) -> None:
    email_str = faker.email(safe=True)
    user = await user_repo.add_user(email_str)

    user_model = await user_service.update_user(user.id, RequestUserUpdateModel(status=UserStatusEnum.BLOCKED.value))

    assert user_model.status == UserStatusEnum.BLOCKED.value


@pytest.mark.asyncio
async def test_update_user_service_fails(
    user_service: UserService, user_repo: FakeUserRepository, faker: Faker
) -> None:
    email_str = faker.email(safe=True)
    user = await user_repo.add_user(email_str)

    with pytest.raises(UserAlreadyActiveException):
        await user_service.update_user(user.id, RequestUserUpdateModel(status=UserStatusEnum.ACTIVE.value))
