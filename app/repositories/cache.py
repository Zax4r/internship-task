from typing import Any

import orjson
from redis.asyncio import Redis


class CacheRepository:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str) -> Any:
        data = await self.redis.get(key)
        return orjson.loads(data) if data else None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        data = orjson.dumps(value)
        await self.redis.set(key, data, ex=ttl)
