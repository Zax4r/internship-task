from typing import Any, Awaitable, Callable

import orjson
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import KafkaError, KafkaTimeoutError
from loguru import logger


class MessageProducerService:
    def __init__(self, producer: AIOKafkaProducer):
        self.producer = producer

    async def send_message(self, topic: str, value: dict[Any, Any]) -> None:
        payload = orjson.dumps(value)
        try:
            await self.producer.send(topic=topic, value=payload)
            logger.info(f'Produced message topic:{topic} payload: {value}')
        except KafkaTimeoutError as exc:
            raise TimeoutError from exc


class MessageConsumerService:
    def __init__(self, consumer: AIOKafkaConsumer):
        self.consumer = consumer

    async def consume(
        self,
        handler: Callable[[dict[str, Any]], Awaitable[Any]],
    ) -> None:
        async for msg in self.consumer:
            try:
                payload = orjson.loads(msg.value)
                logger.info(f'Consumed message topic:{msg.topic} payload:{payload}')
                await handler(payload)
            except orjson.JSONDecodeError as exc:
                logger.error('Failed to decode message: ', exc_info=str(exc))
            except KafkaError as exc:
                logger.error('Kafka error while consuming: ', exc_info=str(exc))
