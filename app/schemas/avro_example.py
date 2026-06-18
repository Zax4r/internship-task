from typing import Optional

from pydantic import BaseModel


class AvroTestDataRequestSchema(BaseModel):
    name: str
    number: Optional[int]
    text: Optional[str]


class AvroModel(BaseModel):
    name: str
    number: Optional[int]
    text: Optional[str]
