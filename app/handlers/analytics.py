from typing import Any

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.redis import redis_client
from app.core.uow import UnitOfWork
from app.repositories.analytics import AnalyticsCacheRepository, AnalyticsRepository
from app.repositories.cache import CacheRepository
from app.services.analytics import AnalyticsService


class AnalyticsMessageHandler:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def __call__(self, payload: dict[str, Any]) -> None:
        action = payload.get('action')
        logger.info(f'Handling analytics action: {action}')
        if action == 'run_analytics':
            async with self.session_factory() as session:
                uow = UnitOfWork(session=session)
                repo = AnalyticsRepository(session=session)
                cache_repo = AnalyticsCacheRepository(CacheRepository(redis_client))
                service = AnalyticsService(uow=uow, analytics_repo=repo, cache_repo=cache_repo)
                data = await service.perform_analysis()
                logger.info(f'Analysis done {data[0]} , {data[1]} results')
        else:
            logger.info(f'Unknown analytics action: {action}')
