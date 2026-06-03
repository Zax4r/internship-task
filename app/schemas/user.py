from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic.v1 import root_validator

from app.core.enums import CurrencyEnum, UserStatusEnum


class RequestUserModel(BaseModel):
    email: str


class RequestUserUpdateModel(BaseModel):
    status: UserStatusEnum


class ResponseUserBalanceModel(BaseModel):
    currency: Optional[CurrencyEnum] = None
    amount: Optional[float] = None


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


class UserBalanceModel(BaseModel):
    id: Optional[int]
    user_id: Optional[int] = None
    currency: Optional[CurrencyEnum] = None
    amount: Optional[float] = None

    @root_validator(pre=True)
    def validate_not_negative(self, values):
        if 'amount' in values and values.get('amount'):
            if values['amount'] < 0:
                raise ValueError('Amount cannot be negative')

        return values
