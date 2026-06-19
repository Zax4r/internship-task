from typing import Any

import orjson

from app.services.coders.base import BaseCoder


class OrjsonCoder(BaseCoder):
    def encode(self, data: dict[Any, Any]) -> bytes:
        return orjson.dumps(data)

    def decode(self, data: bytes) -> dict[Any, Any]:
        return orjson.loads(data)
