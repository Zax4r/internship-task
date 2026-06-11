from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.uow import UnitOfWork
from app.repositories.transaction import TransactionRepository
from app.repositories.user import UserRepository
from app.schemas.transaction import RequestTransactionModel, TransactionModel
from app.services.queries import (
    get_not_rollbacked_deposit_amount,
    get_not_rollbacked_transactions_count,
    get_not_rollbacked_withdraw_amount,
    get_registered_and_deposit_users_count,
    get_registered_and_not_rollbacked_deposit_users_count,
    get_registered_users_count,
    get_transactions_count,
)
from app.services.transaction import TransactionService

router = APIRouter()


def get_transaction_service(session: AsyncSession = Depends(get_async_session)) -> TransactionService:
    uow = UnitOfWork(session=session)
    user_repo = UserRepository(session=session)
    transaction_repo = TransactionRepository(session=session)
    return TransactionService(uow=uow, user_repo=user_repo, transaction_repo=transaction_repo)


@router.get('/transactions', response_model=list[TransactionModel] | None, status_code=status.HTTP_200_OK)
async def get_transactions(
    user_id: Optional[int] = None, service: TransactionService = Depends(get_transaction_service)
) -> list[TransactionModel]:
    return await service.get_transactions(user_id=user_id)


@router.post('/{user_id}/transactions', response_model=Optional[TransactionModel] | None, status_code=status.HTTP_200_OK)
async def post_transaction(
    user_id: int, transaction: RequestTransactionModel, service: TransactionService = Depends(get_transaction_service)
):
    return await service.add_transaction(user_id=user_id, transaction=transaction)


@router.patch('/{user_id}/transactions/{transaction_id}', response_model=Optional[TransactionModel] | None)
async def patch_rollback_transaction(user_id: int, transaction_id: int, service: TransactionService = Depends(get_transaction_service)):
    return await service.patch_rollback_transaction(user_id=user_id, transaction_id=transaction_id)


@router.get('/transactions/analysis', response_model=Optional[list] | None, status_code=status.HTTP_200_OK)
async def get_transaction_analysis(session: AsyncSession = Depends(get_async_session)) -> list[dict]:
    dt_gt = datetime.utcnow().date() - timedelta(weeks=1) + timedelta(days=1)
    dt_lt = datetime.utcnow().date()
    results = []
    for i in range(52):
        registered_users_count = await get_registered_users_count(session, dt_gt=dt_gt, dt_lt=dt_lt)
        registered_and_deposit_users_count = await get_registered_and_deposit_users_count(session, dt_gt=dt_gt, dt_lt=dt_lt)
        registered_and_not_rollbacked_deposit_users_count = await get_registered_and_not_rollbacked_deposit_users_count(
            session, dt_gt=dt_gt, dt_lt=dt_lt
        )
        not_rollbacked_deposit_amount = await get_not_rollbacked_deposit_amount(session, dt_gt=dt_gt, dt_lt=dt_lt)
        not_rollbacked_withdraw_amount = await get_not_rollbacked_withdraw_amount(session, dt_gt=dt_gt, dt_lt=dt_lt)
        transactions_count = await get_transactions_count(session, dt_gt=dt_gt, dt_lt=dt_lt)
        not_rollbacked_transactions_count = await get_not_rollbacked_transactions_count(session, dt_gt=dt_gt, dt_lt=dt_lt)
        result = {
            'start_date': dt_gt,
            'end_date': dt_lt,
            'registered_users_count': registered_users_count,
            'registered_and_deposit_users_count': registered_and_deposit_users_count,
            'registered_and_not_rollbacked_deposit_users_count': registered_and_not_rollbacked_deposit_users_count,
            'not_rollbacked_deposit_amount': not_rollbacked_deposit_amount,
            'not_rollbacked_withdraw_amount': not_rollbacked_withdraw_amount,
            'transactions_count': transactions_count,
            'not_rollbacked_transactions_count': not_rollbacked_transactions_count,
        }
        for field in (
            'registered_users_count',
            'registered_and_deposit_users_count',
            'registered_and_not_rollbacked_deposit_users_count',
            'not_rollbacked_deposit_amount',
            'not_rollbacked_withdraw_amount',
            'transactions_count',
            'not_rollbacked_transactions_count',
        ):
            if result[field] > 0:
                results.append(result)
                break
        dt_gt -= timedelta(weeks=1)
        dt_lt -= timedelta(weeks=1)
    return results
