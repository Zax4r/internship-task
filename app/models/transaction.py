from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import DECIMAL_FRACTIONAL_DIGITS, DECIMAL_TOTAL_DIGITS
from app.core.database import Base


class Transaction(Base):
    __tablename__ = 'transaction'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int]
    currency: Mapped[str]
    amount: Mapped[Decimal] = mapped_column(Numeric(DECIMAL_TOTAL_DIGITS, DECIMAL_FRACTIONAL_DIGITS))
    status: Mapped[str]
    created: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
