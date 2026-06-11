from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str | None] = mapped_column(unique=True)
    status: Mapped[str | None]
    created: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user_balance: Mapped[list['UserBalance']] = relationship('UserBalance', back_populates='owner')


class UserBalance(Base):
    __tablename__ = 'user_balance'
    __table_args__ = (UniqueConstraint('user_id', 'currency', name='user_balance_user_currency_unique'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    currency: Mapped[str | None] = mapped_column(nullable=True)
    amount: Mapped[Decimal | None] = mapped_column(nullable=True)
    created: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    owner: Mapped['User'] = relationship('User', back_populates='user_balance')
