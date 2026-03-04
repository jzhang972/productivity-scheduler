"""Standalone schedule output types — no SQLAlchemy/DB dependencies."""
from __future__ import annotations

import datetime
import uuid
from pydantic import BaseModel


class ScheduleGenerateRequest(BaseModel):
    target_date: datetime.date
    force_regenerate: bool = False


class ScheduledBlock(BaseModel):
    category_id: str
    category_name: str
    color_hex: str
    date: datetime.date
    start_time: datetime.time
    end_time: datetime.time
    planned_duration: int
    title: str | None = None
    is_deep_work: bool = False
    urgency_score: float = 0.0


class ScheduleWarning(BaseModel):
    code: str
    message: str


class SchedulePreviewResponse(BaseModel):
    target_date: datetime.date
    blocks: list[ScheduledBlock]
    total_planned_minutes: int
    warnings: list[ScheduleWarning]
    generated_at: str
