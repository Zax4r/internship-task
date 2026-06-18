from typing import Any

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.redis import redis_client
from app.repositories.avro_example import AvroCacheRepository
from app.repositories.cache import CacheRepository
from app.services.avro_example import AvroExampleService


class AvroExampleHandler:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def __call__(self, payload: dict[str, Any]) -> None:
        action = payload.get('action')
        logger.info(f'Handling avro_example action: {action}')
        try:
            if action == 'test_action':
                cache_repo = AvroCacheRepository(CacheRepository(redis_client))
                service = AvroExampleService(cache_repo=cache_repo)
                await service.store_data(payload)
            else:
                logger.info(f'Unknown analytics action: {action}')
        except Exception as exc:
            logger.error(exc)
