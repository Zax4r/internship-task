from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import DECIMAL_FRACTIONAL_DIGITS, DECIMAL_TOTAL_DIGITS
from app.core.database import Base


class User(Base):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    status: Mapped[str]
    created: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user_balance: Mapped[list['UserBalance']] = relationship('UserBalance', back_populates='owner')


class UserBalance(Base):
    __tablename__ = 'user_balance'
    __table_args__ = (UniqueConstraint('user_id', 'currency', name='user_balance_user_currency_unique'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    currency: Mapped[str]
    amount: Mapped[Decimal] = mapped_column(Numeric(DECIMAL_TOTAL_DIGITS, DECIMAL_FRACTIONAL_DIGITS))
    created: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    owner: Mapped['User'] = relationship('User', back_populates='user_balance')
