from decimal import Decimal

import pytest

from app.core.enums import CurrencyEnum
from app.core.exceptions import (
    CreateTransactionForBlockedUserException,
    NegativeBalanceException,
)
from app.models.user import User
from app.repositories.transaction import FakeTransactionRepository
from app.repositories.user import FakeUserRepository
from app.schemas.transaction import RequestTransactionModel
from app.services.transaction import TransactionService


@pytest.mark.asyncio
async def test_get_transactions_service(
    transaction_service: TransactionService,
    transaction_repo: FakeTransactionRepository,
) -> None:
    transaction1 = await transaction_repo.add_transaction(
        1,
        CurrencyEnum.USD.value,
        Decimal('100.00'),
    )
    transaction2 = await transaction_repo.add_transaction(
        2,
        CurrencyEnum.USD.value,
        Decimal('100.00'),
    )
    transactions = await transaction_service.get_transactions()

    assert len(transactions) == 2
    assert any(x.id == transaction1.id for x in transactions)
    assert any(x.id == transaction2.id for x in transactions)


@pytest.mark.asyncio
async def test_get_transactions_by_user_id_service(
    transaction_service: TransactionService,
    transaction_repo: FakeTransactionRepository,
) -> None:
    transaction1 = await transaction_repo.add_transaction(
        1,
        CurrencyEnum.USD.value,
        Decimal('100.00'),
    )
    transaction2 = await transaction_repo.add_transaction(
        2,
        CurrencyEnum.USD.value,
        Decimal('100.00'),
    )
    transactions = await transaction_service.get_transactions(user_id=1)

    assert len(transactions) == 1
    assert any(x.id == transaction1.id for x in transactions)
    assert not any(x.id == transaction2.id for x in transactions)


@pytest.mark.asyncio
async def test_add_transactions_service(
    transaction_service: TransactionService,
    user_repo: FakeUserRepository,
    active_user: User,
) -> None:
    await transaction_service.add_transaction(
        user_id=active_user.id,
        transaction=RequestTransactionModel(
            currency=CurrencyEnum.USD.value,
            amount=Decimal('100'),
        ),
    )

    new_balance = await user_repo.get_user_balance(active_user.id, CurrencyEnum.USD.value)

    assert new_balance.amount == Decimal('300')


@pytest.mark.asyncio
async def test_add_transactions_service_fails_user_blocked(
    transaction_service: TransactionService,
    blocked_user: User,
) -> None:

    with pytest.raises(CreateTransactionForBlockedUserException):
        await transaction_service.add_transaction(
            user_id=blocked_user.id,
            transaction=RequestTransactionModel(
                currency=CurrencyEnum.USD.value,
                amount=Decimal('100'),
            ),
        )


@pytest.mark.asyncio
async def test_add_transactions_service_fails_neg_balance(
    transaction_service: TransactionService,
    active_user: User,
) -> None:

    with pytest.raises(NegativeBalanceException):
        await transaction_service.add_transaction(
            user_id=active_user.id,
            transaction=RequestTransactionModel(
                currency=CurrencyEnum.USD.value,
                amount=Decimal('-1000'),
            ),
        )


@pytest.mark.asyncio
async def test_rollback_transaction_service(
    transaction_service: TransactionService,
    user_repo: FakeUserRepository,
    active_user: User,
) -> None:
    transaction = await transaction_service.add_transaction(
        user_id=active_user.id,
        transaction=RequestTransactionModel(
            currency=CurrencyEnum.USD.value,
            amount=Decimal('100'),
        ),
    )

    await transaction_service.patch_rollback_transaction(active_user.id, transaction.id)
    user_balance = await user_repo.get_user_balance(active_user.id, CurrencyEnum.USD.value)

    assert user_balance.amount == Decimal('200')


@pytest.mark.asyncio
async def test_rollback_transaction_service_fails(
    transaction_service: TransactionService,
    transaction_repo: FakeTransactionRepository,
    user_repo: FakeUserRepository,
    active_user: User,
) -> None:
    transaction = await transaction_repo.add_transaction(
        active_user.id,
        CurrencyEnum.USD.value,
        Decimal('1000'),
    )

    with pytest.raises(NegativeBalanceException):
        await transaction_service.patch_rollback_transaction(active_user.id, transaction.id)
