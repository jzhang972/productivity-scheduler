from __future__ import annotations

import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, Field, model_validator
from app.enums import BlockStatus
from app.schemas.category import CategoryRead


class TimeBlockBase(BaseModel):
    category_id: uuid.UUID
    date: datetime.date
    start_time: datetime.time
    end_time: datetime.time
    planned_duration: int = Field(..., gt=0)
    title: Optional[str] = Field(default=None, max_length=200)
    notes: Optional[str] = None

    @model_validator(mode="after")
    def end_after_start(self) -> TimeBlockBase:
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class TimeBlockCreate(TimeBlockBase):
    pass


class TimeBlockUpdate(BaseModel):
    category_id: Optional[uuid.UUID] = None
    date: Optional[datetime.date] = None
    start_time: Optional[datetime.time] = None
    end_time: Optional[datetime.time] = None
    planned_duration: Optional[int] = Field(default=None, gt=0)
    title: Optional[str] = Field(default=None, max_length=200)
    notes: Optional[str] = None


class TimeBlockStatusUpdate(BaseModel):
    status: BlockStatus


class TimeBlockRead(TimeBlockBase):
    id: uuid.UUID
    status: BlockStatus
    category: CategoryRead
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}
