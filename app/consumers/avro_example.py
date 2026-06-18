from aiokafka import AIOKafkaConsumer

from app.core.config import settings
from app.core.constants import AVRO_TEST_SCHEMA_PATH
from app.core.database import async_session_maker
from app.core.enums import KafkaTopicEnum
from app.handlers.avro_example import AvroExampleHandler
from app.services.coders.avr import AvroCoder
from app.services.message import MessageConsumerService


class AvroConsumer:
    topic = KafkaTopicEnum.AVRO.value

    def __init__(self, handler: AvroExampleHandler):
        self.handler = handler
        self.service: MessageConsumerService | None = None

    async def start(self) -> None:
        raw_consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=settings.KAFKA_URL,
        )
        coder = AvroCoder(AVRO_TEST_SCHEMA_PATH)
        await raw_consumer.start()
        self.service = MessageConsumerService(coder=coder, consumer=raw_consumer)
        await self.service.consume(self.handler)

    async def stop(self) -> None:
        if self.service:
            await self.service.consumer.stop()


async def get_avro_consumer() -> AvroConsumer:
    handler = AvroExampleHandler(session_factory=async_session_maker)
    return AvroConsumer(handler=handler)
