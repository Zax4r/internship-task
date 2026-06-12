from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import settings
from app.core.database import Base


class Transaction(Base):
    __tablename__ = 'transaction'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int]
    currency: Mapped[str]
    amount: Mapped[Decimal] = mapped_column(Numeric(settings.DECIMAL_TOTAL_DIGITS, settings.DECIMAL_FRACTIONAL_DIGITS))
    status: Mapped[str]
    created: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
