from abc import ABC, abstractmethod
from typing import Any


class BaseCoder(ABC):
    @abstractmethod
    def encode(self, data: dict[Any, Any]) -> bytes: ...

    @abstractmethod
    def decode(self, data: bytes) -> dict[Any, Any]: ...
