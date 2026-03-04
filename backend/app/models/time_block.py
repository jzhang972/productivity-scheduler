from __future__ import annotations
import uuid
from datetime import datetime, date, time, timezone
from sqlalchemy import (
    String, Integer, Text, ForeignKey, Date, Time,
    DateTime, CheckConstraint, Enum as SAEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
from app.enums import BlockStatus


class TimeBlock(Base):
    __tablename__ = "time_blocks"
    __table_args__ = (
        CheckConstraint("end_time > start_time", name="chk_end_after_start"),
        CheckConstraint("planned_duration > 0", name="chk_positive_duration"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    planned_duration: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[BlockStatus] = mapped_column(
        SAEnum(BlockStatus, name="block_status", create_type=True),
        nullable=False,
        default=BlockStatus.planned,
        index=True,
    )
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    category: Mapped["Category"] = relationship(
        "Category", back_populates="time_blocks", lazy="joined"
    )
    time_logs: Mapped[list["TimeLog"]] = relationship(
        "TimeLog", back_populates="time_block", cascade="all, delete-orphan", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<TimeBlock(id={self.id}, date={self.date}, status={self.status})>"
