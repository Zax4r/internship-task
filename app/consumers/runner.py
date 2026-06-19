import asyncio

from app.consumers.base import MessageConsumer


class ConsumerRunner:
    def __init__(self, consumers: list[MessageConsumer]):
        self.consumers = consumers
        self.tasks: list[asyncio.Task] = []

    async def start(self) -> None:
        for consumer in self.consumers:
            await consumer.__aenter__()
            task = asyncio.create_task(consumer.consume())
            self.tasks.append(task)

    async def stop(self) -> None:
        for task in self.tasks:
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)

        for consumer in self.consumers:
            await consumer.__aexit__(None, None, None)
