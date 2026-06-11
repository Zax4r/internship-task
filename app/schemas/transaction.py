from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.enums import CurrencyEnum, TransactionStatusEnum


class RequestTransactionModel(BaseModel):
    currency: CurrencyEnum
    amount: float


class TransactionModel(BaseModel):
    id: int | None
    user_id: int | None = None
    currency: CurrencyEnum | None = None
    amount: float | None = None
    status: TransactionStatusEnum | None = None
    created: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
