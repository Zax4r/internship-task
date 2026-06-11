from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Transaction(Base):
    __tablename__ = 'transaction'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int]
    currency: Mapped[str | None]
    amount: Mapped[Decimal | None]
    status: Mapped[str | None]
    created: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
