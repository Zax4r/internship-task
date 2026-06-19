from typing import Any

from app.core.exceptions import TestDataNotFoundException
from app.repositories.avro_example import AvroCacheRepository
from app.schemas.avro_example import AvroModel


class AvroExampleService:
    def __init__(self, cache_repo: AvroCacheRepository):
        self.cache_repo = cache_repo

    async def get_report(self) -> AvroModel:
        report = await self.cache_repo.get_report()
        if not report:
            raise TestDataNotFoundException(detail='No data found in Redis')
        results = AvroModel(**report)
        return results

    async def store_data(self, data: dict[Any, Any]) -> None:
        await self.cache_repo.set_report(data)
