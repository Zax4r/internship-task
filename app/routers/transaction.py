from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.uow import UnitOfWork
from app.repositories.analytics import AnalyticsRepository
from app.repositories.transaction import TransactionRepository
from app.repositories.user import UserRepository
from app.schemas.analytics import AnalysisModel
from app.schemas.transaction import RequestTransactionModel, TransactionModel
from app.services.transaction import TransactionService

router = APIRouter()


def get_transaction_service(session: AsyncSession = Depends(get_async_session)) -> TransactionService:
    uow = UnitOfWork(session=session)
    user_repo = UserRepository(session=session)
    transaction_repo = TransactionRepository(session=session)
    analytics_repo = AnalyticsRepository(session=session)
    return TransactionService(uow=uow, user_repo=user_repo, transaction_repo=transaction_repo, analytics_repo=analytics_repo)


@router.get('/transactions', response_model=list[TransactionModel], status_code=status.HTTP_200_OK)
async def get_transactions(
    user_id: Optional[int] = None, service: TransactionService = Depends(get_transaction_service)
) -> list[TransactionModel]:
    return await service.get_transactions(user_id=user_id)


@router.post('/{user_id}/transactions', response_model=TransactionModel, status_code=status.HTTP_200_OK)
async def post_transaction(
    user_id: int, transaction: RequestTransactionModel, service: TransactionService = Depends(get_transaction_service)
) -> TransactionModel:
    return await service.add_transaction(user_id=user_id, transaction=transaction)


@router.patch('/{user_id}/transactions/{transaction_id}', response_model=TransactionModel)
async def patch_rollback_transaction(
    user_id: int, transaction_id: int, service: TransactionService = Depends(get_transaction_service)
) -> TransactionModel:
    return await service.patch_rollback_transaction(user_id=user_id, transaction_id=transaction_id)


@router.get('/transactions/analysis', response_model=list[AnalysisModel], status_code=status.HTTP_200_OK)
async def get_transaction_analysis(service: TransactionService = Depends(get_transaction_service)) -> list[AnalysisModel]:
    return await service.transaction_analysis()
