from __future__ import annotations

import datetime
import uuid
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class DailyReviewBase(BaseModel):
    date: datetime.date
    energy_rating: int = Field(..., ge=1, le=5)
    sleep_hours: Decimal = Field(..., ge=0, le=24, decimal_places=1)
    gym_done: bool = False
    notes: Optional[str] = None


class DailyReviewCreate(DailyReviewBase):
    pass


class DailyReviewUpdate(BaseModel):
    energy_rating: Optional[int] = Field(default=None, ge=1, le=5)
    sleep_hours: Optional[Decimal] = Field(default=None, ge=0, le=24)
    gym_done: Optional[bool] = None
    notes: Optional[str] = None


class DailyReviewRead(DailyReviewBase):
    id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}
