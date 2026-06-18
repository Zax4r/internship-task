from typing import Any

from app.repositories.cache import CacheRepository


class AvroCacheRepository:
    AVRO_CACHE_KEY = 'avro_example'
    AVRO_TTL = 3600

    def __init__(self, cache: CacheRepository):
        self.cache = cache

    async def get_report(self) -> dict[str, Any] | None:
        data = await self.cache.get(self.AVRO_CACHE_KEY)
        return data

    async def set_report(self, report: dict[str, Any]) -> None:
        await self.cache.set(self.AVRO_CACHE_KEY, report, self.AVRO_TTL)
