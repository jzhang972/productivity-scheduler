from __future__ import annotations
import uuid
from datetime import datetime, date, timezone
from decimal import Decimal
from sqlalchemy import SmallInteger, Numeric, Boolean, Text, Date, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class DailyReview(Base):
    __tablename__ = "daily_reviews"
    __table_args__ = (
        CheckConstraint("energy_rating BETWEEN 1 AND 5", name="chk_energy_rating"),
        CheckConstraint("sleep_hours BETWEEN 0 AND 24", name="chk_sleep_hours"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, unique=True, index=True)
    energy_rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    sleep_hours: Mapped[Decimal] = mapped_column(Numeric(3, 1), nullable=False)
    gym_done: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return f"<DailyReview(id={self.id}, date={self.date}, energy={self.energy_rating})>"
