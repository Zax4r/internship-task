from typing import Any

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaTimeoutError
from loguru import logger

from app.services.coders.base import BaseCoder


class MessageProducerService:
    def __init__(self, coder: BaseCoder, producer: AIOKafkaProducer):
        self.coder = coder
        self.producer = producer

    async def send_message(self, topic: str, value: dict[Any, Any]) -> None:
        payload = self.coder.encode(value)
        try:
            await self.producer.send(topic=topic, value=payload)
            logger.info(f'Produced message topic:{topic} payload: {value}')
        except KafkaTimeoutError as exc:
            raise TimeoutError from exc
