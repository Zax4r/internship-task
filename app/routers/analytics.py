from typing import AsyncGenerator

from aiokafka import AIOKafkaProducer
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_async_session
from app.core.enums import KafkaTopicEnum
from app.core.uow import UnitOfWork
from app.repositories.analytics import AnalyticsRepository
from app.services.analytics import AnalyticsService
from app.services.message import MessageProducerService

router = APIRouter()


async def get_message_producer_service() -> AsyncGenerator[MessageProducerService, None]:
    producer = AIOKafkaProducer(bootstrap_servers=settings.KAFKA_URL)
    await producer.start()
    try:
        yield MessageProducerService(producer=producer)
    finally:
        await producer.stop()


def get_analytics_service(session: AsyncSession = Depends(get_async_session)) -> AnalyticsService:
    uow = UnitOfWork(session=session)
    analytics_repo = AnalyticsRepository(session=session)
    return AnalyticsService(uow=uow, analytics_repo=analytics_repo)


@router.get('/analytics', response_model=None, status_code=status.HTTP_200_OK)
async def start_analysis(
    service: MessageProducerService = Depends(get_message_producer_service),
) -> None:
    payload = {'action': 'run_analytics'}
    return await service.send_message(KafkaTopicEnum.ANALYTICS.value, payload)
