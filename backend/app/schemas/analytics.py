from __future__ import annotations
from datetime import date
from pydantic import BaseModel


class CategoryDailyTotal(BaseModel):
    category_id: str
    category_name: str
    color_hex: str
    total_minutes: int


class DailyTotalsRead(BaseModel):
    date: date
    totals: list[CategoryDailyTotal]
    total_minutes: int


class CategoryWeeklyProgress(BaseModel):
    category_id: str
    category_name: str
    color_hex: str
    weekly_target_minutes: int
    actual_minutes: int
    planned_minutes: int
    deficit_minutes: int
    completion_pct: float


class WeeklyProgressRead(BaseModel):
    week_start: date
    week_end: date
    categories: list[CategoryWeeklyProgress]
    total_actual_minutes: int
    total_planned_minutes: int


class HourBucket(BaseModel):
    hour: int
    avg_minutes: float
    sample_count: int


class BestHoursRead(BaseModel):
    hours: list[HourBucket]


class DeepWorkDay(BaseModel):
    date: date
    deep_work_minutes: int
    total_minutes: int


class DeepWorkTrendRead(BaseModel):
    days: list[DeepWorkDay]
    avg_deep_work_minutes: float
    max_deep_work_minutes: int
