from aiokafka import AIOKafkaConsumer

from app.core.config import settings
from app.core.database import async_session_maker
from app.core.enums import KafkaTopicEnum
from app.handlers.analytics import AnalyticsMessageHandler
from app.services.message import MessageConsumerService


class AnalyticsConsumer:
    topic = KafkaTopicEnum.ANALYTICS.value

    def __init__(self, handler: AnalyticsMessageHandler):
        self.handler = handler
        self.service: MessageConsumerService | None = None

    async def start(self) -> None:
        raw_consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=settings.KAFKA_URL,
        )
        await raw_consumer.start()
        self.service = MessageConsumerService(consumer=raw_consumer)
        await self.service.consume(self.handler)

    async def stop(self) -> None:
        if self.service:
            await self.service.consumer.stop()


async def get_analytics_consumer() -> AnalyticsConsumer:
    handler = AnalyticsMessageHandler(session_factory=async_session_maker)
    return AnalyticsConsumer(handler=handler)
