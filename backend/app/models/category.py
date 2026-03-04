from __future__ import annotations
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, SmallInteger, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    color_hex: Mapped[str] = mapped_column(String(7), nullable=False, default="#6366f1")
    priority_weight: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    weekly_target_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    daily_cap_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_deep_work: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    time_blocks: Mapped[list["TimeBlock"]] = relationship(
        "TimeBlock", back_populates="category", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name={self.name})>"
