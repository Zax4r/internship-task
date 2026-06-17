from aiokafka import AIOKafkaConsumer

from app.core.config import settings
from app.core.database import async_session_maker
from app.core.enums import KafkaTopicEnum
from app.handlers.analytics import AnalyticsMessageHandler
from app.repositories.analytics import AnalyticsRepository
from app.services.analytics import AnalyticsService
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


def build_analytics_consumer() -> AnalyticsConsumer:
    session = async_session_maker()
    analytics_repo = AnalyticsRepository(session=session)
    analytics_service = AnalyticsService(analytics_repo=analytics_repo)
    handler = AnalyticsMessageHandler(analytics_service=analytics_service)
    return AnalyticsConsumer(handler=handler)
