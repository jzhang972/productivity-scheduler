from __future__ import annotations
import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class TimeLogCreate(BaseModel):
    time_block_id: uuid.UUID
    notes: str | None = None


class TimeLogStop(BaseModel):
    interruptions: int = Field(default=0, ge=0)
    notes: str | None = None


class TimeLogUpdate(BaseModel):
    interruptions: int | None = Field(default=None, ge=0)
    notes: str | None = None
    actual_end: datetime | None = None
    actual_duration: int | None = Field(default=None, ge=0)


class TimeLogRead(BaseModel):
    id: uuid.UUID
    time_block_id: uuid.UUID
    actual_start: datetime
    actual_end: datetime | None
    actual_duration: int | None
    interruptions: int
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
