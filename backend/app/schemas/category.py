from __future__ import annotations
import uuid
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    color_hex: str = Field(default="#6366f1", pattern=r"^#[0-9A-Fa-f]{6}$")
    priority_weight: int = Field(default=1, ge=1, le=10)
    weekly_target_minutes: int = Field(default=0, ge=0)
    daily_cap_minutes: int | None = Field(default=None, ge=1)
    is_deep_work: bool = False
    is_active: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    color_hex: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")
    priority_weight: int | None = Field(default=None, ge=1, le=10)
    weekly_target_minutes: int | None = Field(default=None, ge=0)
    daily_cap_minutes: int | None = Field(default=None, ge=1)
    is_deep_work: bool | None = None
    is_active: bool | None = None


class CategoryRead(CategoryBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
