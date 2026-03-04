from __future__ import annotations
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryRead
from app.schemas.time_block import TimeBlockCreate, TimeBlockUpdate, TimeBlockRead, TimeBlockStatusUpdate
from app.schemas.time_log import TimeLogCreate, TimeLogRead, TimeLogStop, TimeLogUpdate
from app.schemas.daily_review import DailyReviewCreate, DailyReviewUpdate, DailyReviewRead
from app.schemas.analytics import (
    DailyTotalsRead, WeeklyProgressRead, BestHoursRead, DeepWorkTrendRead
)
from app.schemas.schedule import ScheduleGenerateRequest, SchedulePreviewResponse

__all__ = [
    "CategoryCreate", "CategoryUpdate", "CategoryRead",
    "TimeBlockCreate", "TimeBlockUpdate", "TimeBlockRead", "TimeBlockStatusUpdate",
    "TimeLogCreate", "TimeLogRead", "TimeLogStop", "TimeLogUpdate",
    "DailyReviewCreate", "DailyReviewUpdate", "DailyReviewRead",
    "DailyTotalsRead", "WeeklyProgressRead", "BestHoursRead", "DeepWorkTrendRead",
    "ScheduleGenerateRequest", "SchedulePreviewResponse",
]
