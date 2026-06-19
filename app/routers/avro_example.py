from typing import AsyncGenerator

from fastapi import APIRouter, Depends, status

from app.core.constants import AVRO_TEST_SCHEMA_PATH
from app.core.enums import KafkaTopicEnum
from app.core.redis import redis_client
from app.producers.message import MessageProducer
from app.repositories.avro_example import AvroCacheRepository
from app.repositories.cache import CacheRepository
from app.schemas.avro_example import AvroModel, AvroTestDataRequestSchema
from app.services.avro_example import AvroExampleService
from app.services.coders.avr import AvroCoder

router = APIRouter()


async def get_message_producer_service() -> AsyncGenerator[MessageProducer, None]:
    coder = AvroCoder(AVRO_TEST_SCHEMA_PATH)
    message_producer = MessageProducer(coder=coder)
    async with message_producer as mp:
        yield mp


def get_avro_service() -> AvroExampleService:
    cache_repo = AvroCacheRepository(CacheRepository(redis_client))
    return AvroExampleService(cache_repo=cache_repo)


@router.post('/avro-example-start', response_model=None, status_code=status.HTTP_200_OK)
async def analytics_start(
    test_data: AvroTestDataRequestSchema,
    service: MessageProducer = Depends(get_message_producer_service),
) -> None:
    payload = {'action': 'test_action', **test_data.model_dump()}
    return await service.send_message(KafkaTopicEnum.AVRO.value, payload)


@router.get('/avro-example-data', response_model=AvroModel, status_code=status.HTTP_200_OK)
async def analytics_report(
    service: AvroExampleService = Depends(get_avro_service),
) -> AvroModel:
    return await service.get_report()
