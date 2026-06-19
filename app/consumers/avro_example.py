from app.consumers.base import MessageConsumer
from app.core.constants import AVRO_TEST_SCHEMA_PATH
from app.core.enums import KafkaTopicEnum
from app.handlers.avro_example import AvroExampleHandler
from app.services.coders.avr import AvroCoder
from app.services.coders.base import BaseCoder


class AvroConsumer(MessageConsumer):
    _topic = KafkaTopicEnum.AVRO

    def __init__(self, coder: BaseCoder, handler: AvroExampleHandler):
        super().__init__(coder, handler)


def get_avro_consumer() -> AvroConsumer:
    handler = AvroExampleHandler()
    coder = AvroCoder(AVRO_TEST_SCHEMA_PATH)
    return AvroConsumer(coder=coder, handler=handler)
