from __future__ import annotations
import uuid
from datetime import datetime, timezone
from sqlalchemy import Integer, SmallInteger, Text, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class TimeLog(Base):
    __tablename__ = "time_logs"
    __table_args__ = (
        CheckConstraint(
            "actual_duration IS NULL OR actual_duration >= 0",
            name="chk_non_negative_duration"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    time_block_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("time_blocks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    actual_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    actual_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    actual_duration: Mapped[int | None] = mapped_column(Integer, nullable=True)
    interruptions: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    time_block: Mapped["TimeBlock"] = relationship(
        "TimeBlock", back_populates="time_logs", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<TimeLog(id={self.id}, block={self.time_block_id}, active={self.actual_end is None})>"
