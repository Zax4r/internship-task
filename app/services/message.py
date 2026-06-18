from typing import Any, Awaitable, Callable

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import KafkaError, KafkaTimeoutError
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


class MessageConsumerService:
    def __init__(self, coder: BaseCoder, consumer: AIOKafkaConsumer):
        self.coder = coder
        self.consumer = consumer

    async def consume(
        self,
        handler: Callable[[dict[str, Any]], Awaitable[Any]],
    ) -> None:
        async for msg in self.consumer:
            try:
                payload = self.coder.decode(msg.value)
                logger.info(f'Consumed message topic:{msg.topic} payload:{payload}')
                await handler(payload)
            except KafkaError as exc:
                logger.error('Kafka error while consuming: ', exc_info=str(exc))
