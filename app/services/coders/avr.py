import io
from typing import Any

import avro.io
import avro.schema

from app.services.coders.base import BaseCoder


class AvroCoder(BaseCoder):
    def __init__(self, schema_path: str):
        self.schema_path = schema_path
        self.schema = avro.schema.parse(open(schema_path).read())

    def encode(self, data: dict[Any, Any]) -> bytes:
        writer = avro.io.DatumWriter(self.schema)
        bytes_writer = io.BytesIO()
        encoder = avro.io.BinaryEncoder(bytes_writer)
        writer.write(data, encoder)
        raw_bytes = bytes_writer.getvalue()
        return raw_bytes

    def decode(self, data: bytes) -> dict[Any, Any]:
        bytes_reader = io.BytesIO(data)
        decoder = avro.io.BinaryDecoder(bytes_reader)
        reader = avro.io.DatumReader(self.schema)
        obj = reader.read(decoder)
        return obj  # type: ignore[return-value]
