from types import TracebackType
from typing import Any, Awaitable, Callable

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError
from loguru import logger

from app.core.config import settings
from app.core.enums import KafkaGroupEnum, KafkaTopicEnum
from app.services.coders.base import BaseCoder


class MessageConsumer:
    _topic: KafkaTopicEnum | None = None
    _group_id: KafkaGroupEnum | None = None

    def __init__(
        self,
        coder: BaseCoder,
        handler: Callable[[dict[str, Any]], Awaitable[Any]],
    ):
        self.coder = coder
        self.handler = handler
        self.consumer = AIOKafkaConsumer(
            self._topic,
            group_id=self._group_id,
            bootstrap_servers=settings.KAFKA_URL,
            enable_auto_commit=False,
        )

    async def consume(
        self,
    ) -> None:
        async for msg in self.consumer:
            try:
                payload = self.coder.decode(msg.value)
                logger.info(f'Consumed message topic:{msg.topic} payload:{payload}')
                await self.handler(payload)
                await self.consumer.commit()
            except KafkaError as exc:
                logger.error('Kafka error while consuming: ', exc_info=str(exc))
            except Exception as e:
                logger.error(f'Consumer unexpected error committed: {e}')
                raise e

    async def __aenter__(self) -> 'MessageConsumer':
        await self.consumer.start()
        logger.info(f'Started consumer for topic {self._topic}')
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.consumer.stop()
        logger.info(f'Closed consumer for topic {self._topic}')
