from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.core.enums import CurrencyEnum, TransactionStatusEnum


class RequestTransactionModel(BaseModel):
    currency: CurrencyEnum
    amount: Decimal


class TransactionModel(BaseModel):
    id: Optional[int]
    user_id: Optional[int] = None
    currency: Optional[CurrencyEnum] = None
    amount: Optional[Decimal] = None
    status: Optional[TransactionStatusEnum] = None
    created: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
