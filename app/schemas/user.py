from datetime import datetime

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
    user_id: int | None = None
    email: str | None = None
    user_status: str | None = None


class RequestUserUpdateModel(BaseModel):
    status: UserStatusEnum


class ResponseUserBalanceModel(BaseModel):
    currency: CurrencyEnum | None = None
    amount: float | None = None


class ResponseUserModel(BaseModel):
    id: int | None
    email: str | None = None
    status: UserStatusEnum | None = None
    created: datetime | None = None
    balances: list[ResponseUserBalanceModel | None] = None


class UserModel(BaseModel):
    id: int | None
    email: str | None = None
    status: UserStatusEnum | None = None
    created: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class UserBalanceModel(BaseModel):
    id: int | None
    user_id: int | None = None
    currency: CurrencyEnum | None = None
    amount: float | None = None

    @field_validator('amount', mode='before')
    @classmethod
    def validate_not_negative(cls, value: float) -> float:
        if value < 0:
            raise ValueError('Amount cannot be negative')

        return value
