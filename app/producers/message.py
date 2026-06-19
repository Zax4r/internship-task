from types import TracebackType
from typing import Any

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaTimeoutError
from loguru import logger

from app.core.config import settings
from app.services.coders.base import BaseCoder


class MessageProducer:
    def __init__(self, coder: BaseCoder):
        self.coder = coder
        self.producer = AIOKafkaProducer(bootstrap_servers=settings.KAFKA_URL)

    async def send_message(self, topic: str, value: dict[Any, Any]) -> None:
        payload = self.coder.encode(value)
        try:
            await self.producer.send(topic=topic, value=payload)
            logger.info(f'Produced message topic:{topic} payload: {value}')
        except KafkaTimeoutError as exc:
            raise TimeoutError from exc

    async def __aenter__(self) -> 'MessageProducer':
        await self.producer.start()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.producer.stop()
