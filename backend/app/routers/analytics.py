from datetime import date, timedelta
from fastapi import APIRouter, Query
from app.dependencies import DB
from app.services.analytics import (
    get_daily_totals,
    get_weekly_progress,
    get_best_hours,
    get_deep_work_trend,
)
from app.schemas.analytics import (
    DailyTotalsRead,
    WeeklyProgressRead,
    BestHoursRead,
    DeepWorkTrendRead,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/daily-totals", response_model=list[DailyTotalsRead])
async def daily_totals(
    db: DB,
    start: date = Query(...),
    end: date = Query(...),
):
    return await get_daily_totals(db, start, end)


@router.get("/weekly-progress", response_model=WeeklyProgressRead)
async def weekly_progress(
    db: DB,
    week_start: date = Query(..., description="ISO Monday of the target week"),
):
    return await get_weekly_progress(db, week_start)


@router.get("/best-hours", response_model=BestHoursRead)
async def best_hours(
    db: DB,
    days: int = Query(default=30, ge=7, le=90),
):
    return await get_best_hours(db, days)


@router.get("/deep-work-trend", response_model=DeepWorkTrendRead)
async def deep_work_trend(
    db: DB,
    days: int = Query(default=14, ge=7, le=90),
):
    return await get_deep_work_trend(db, days)
