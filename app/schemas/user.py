from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from app.core.enums import CurrencyEnum, UserStatusEnum


class RequestUserModel(BaseModel):
    email: str

    @field_validator('email', mode='before')
    @classmethod
    def ensure_email(cls, value: str) -> str:
        email = value.strip()
        email = ''.join([x for x in email if x != ' '])
        if len(email) == 0:
            raise ValueError("Email can't consist entirely of spaces")
        return email


class RequestListUserModel(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None
    user_status: Optional[str] = None


class RequestUserUpdateModel(BaseModel):
    status: UserStatusEnum


class ResponseUserBalanceModel(BaseModel):
    currency: Optional[CurrencyEnum] = None
    amount: Optional[Decimal] = None


class ResponseUserModel(BaseModel):
    id: Optional[int]
    email: Optional[str] = None
    status: Optional[UserStatusEnum] = None
    created: Optional[datetime] = None
    balances: Optional[list[ResponseUserBalanceModel]] = None


class UserModel(BaseModel):
    id: Optional[int]
    email: Optional[str] = None
    status: Optional[UserStatusEnum] = None
    created: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserBalanceModel(BaseModel):
    id: Optional[int]
    user_id: Optional[int] = None
    currency: Optional[CurrencyEnum] = None
    amount: Optional[Decimal] = None

    @field_validator('amount', mode='before')
    @classmethod
    def validate_not_negative(cls, value: Decimal) -> Decimal:
        if value < 0:
            raise ValueError('Amount cannot be negative')

        return value
