from app.consumers.base import MessageConsumer
from app.core.database import async_session_maker
from app.core.enums import KafkaTopicEnum
from app.handlers.analytics import AnalyticsMessageHandler
from app.services.coders.base import BaseCoder
from app.services.coders.orj import OrjsonCoder


class AnalyticsConsumer(MessageConsumer):
    _topic = KafkaTopicEnum.ANALYTICS

    def __init__(self, coder: BaseCoder, handler: AnalyticsMessageHandler):
        super().__init__(coder, handler)


def get_analytics_consumer() -> AnalyticsConsumer:
    handler = AnalyticsMessageHandler(session_factory=async_session_maker)
    coder = OrjsonCoder()
    return AnalyticsConsumer(coder=coder, handler=handler)
