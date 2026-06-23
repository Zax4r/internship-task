from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.repositories.transaction.sql import SQLTransactionRepository
from app.repositories.uow.sql import SQLUnitOfWork
from app.repositories.user.sql import SQLUserRepository
from app.schemas.transaction import RequestTransactionModel, TransactionModel
from app.services.transaction import TransactionService

router = APIRouter()


def get_transaction_service(
    session: AsyncSession = Depends(get_async_session),
) -> TransactionService:
    uow = SQLUnitOfWork(session=session)
    user_repo = SQLUserRepository(session=session)
    transaction_repo = SQLTransactionRepository(session=session)
    return TransactionService(
        uow=uow,
        user_repo=user_repo,
        transaction_repo=transaction_repo,
    )


@router.get('/transactions', response_model=list[TransactionModel], status_code=status.HTTP_200_OK)
async def get_transactions(
    user_id: Optional[int] = None, service: TransactionService = Depends(get_transaction_service)
) -> list[TransactionModel]:
    return await service.get_transactions(user_id=user_id)


@router.post('/{user_id}/transactions', response_model=TransactionModel, status_code=status.HTTP_201_CREATED)
async def post_transaction(
    user_id: int,
    transaction: RequestTransactionModel,
    service: TransactionService = Depends(get_transaction_service),
) -> TransactionModel:
    return await service.add_transaction(user_id=user_id, transaction=transaction)


@router.patch('/{user_id}/transactions/{transaction_id}', response_model=TransactionModel)
async def patch_rollback_transaction(
    user_id: int,
    transaction_id: int,
    service: TransactionService = Depends(get_transaction_service),
) -> TransactionModel:
    return await service.patch_rollback_transaction(user_id=user_id, transaction_id=transaction_id)
