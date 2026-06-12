from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Transaction(Base):
    __tablename__ = 'transaction'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int]
    currency: Mapped[str]
    amount: Mapped[float]
    status: Mapped[str]
    created: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
