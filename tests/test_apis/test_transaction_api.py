import pytest
from httpx import AsyncClient

from app.core.enums import CurrencyEnum, TransactionStatusEnum
from app.models.transaction import Transaction
from app.models.user import User
from app.repositories.transaction.memory import FakeTransactionRepository
from main import app


@pytest.mark.asyncio
async def test_get_transaction(
    client: AsyncClient,
    transaction_repo: FakeTransactionRepository,
    transaction: Transaction,
) -> None:
    url = app.url_path_for('get_transactions')

    response = await client.get(url)

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]['id'] == transaction.id


@pytest.mark.asyncio
async def test_post_transaction(
    client: AsyncClient,
    transaction_repo: FakeTransactionRepository,
    active_user: User,
) -> None:
    url = app.url_path_for('post_transaction', user_id=active_user.id)

    response = await client.post(
        url,
        json={
            'user_id': active_user.id,
            'currency': CurrencyEnum.USD.value,
            'amount': '100.00',
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data['id']

    transaction_id = data['id']

    assert await transaction_repo.get_transaction_by_id(transaction_id)


@pytest.mark.asyncio
async def test_patch_transaction(
    client: AsyncClient,
    transaction_repo: FakeTransactionRepository,
    transaction: Transaction,
    active_user: User,
) -> None:
    url = app.url_path_for('patch_rollback_transaction', user_id=active_user.id, transaction_id=transaction.id)

    response = await client.patch(url)

    assert response.status_code == 200

    transaction_db = await transaction_repo.get_transaction_by_id(transaction.id)

    assert transaction_db.status == TransactionStatusEnum.ROLLBACKED.value
