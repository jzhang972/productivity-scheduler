"""Analytics computation service."""
from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.time_block import TimeBlock
from app.enums import BlockStatus
from app.models.time_log import TimeLog
from app.schemas.analytics import (
    DailyTotalsRead, CategoryDailyTotal,
    WeeklyProgressRead, CategoryWeeklyProgress,
    BestHoursRead, HourBucket,
    DeepWorkTrendRead, DeepWorkDay,
)


async def get_daily_totals(
    db: AsyncSession, start: date, end: date
) -> list[DailyTotalsRead]:
    stmt = (
        select(
            TimeBlock.date,
            Category.id,
            Category.name,
            Category.color_hex,
            func.sum(TimeBlock.planned_duration).label("total_minutes"),
        )
        .join(Category, TimeBlock.category_id == Category.id)
        .where(
            and_(
                TimeBlock.date >= start,
                TimeBlock.date <= end,
                TimeBlock.status == BlockStatus.done,
            )
        )
        .group_by(TimeBlock.date, Category.id, Category.name, Category.color_hex)
        .order_by(TimeBlock.date)
    )
    rows = (await db.execute(stmt)).all()

    by_date: dict[date, list[CategoryDailyTotal]] = defaultdict(list)
    for row in rows:
        by_date[row.date].append(CategoryDailyTotal(
            category_id=str(row.id),
            category_name=row.name,
            color_hex=row.color_hex,
            total_minutes=row.total_minutes or 0,
        ))

    result = []
    for d, totals in sorted(by_date.items()):
        result.append(DailyTotalsRead(
            date=d,
            totals=totals,
            total_minutes=sum(t.total_minutes for t in totals),
        ))
    return result


async def get_weekly_progress(
    db: AsyncSession, week_start: date
) -> WeeklyProgressRead:
    week_end = week_start + timedelta(days=6)

    # Actual done minutes per category this week
    done_stmt = (
        select(
            Category.id,
            Category.name,
            Category.color_hex,
            Category.weekly_target_minutes,
            func.coalesce(func.sum(TimeBlock.planned_duration), 0).label("actual_minutes"),
        )
        .join(TimeBlock, TimeBlock.category_id == Category.id, isouter=True)
        .where(
            and_(
                TimeBlock.date >= week_start,
                TimeBlock.date <= week_end,
                TimeBlock.status == BlockStatus.done,
            )
        )
        .group_by(Category.id, Category.name, Category.color_hex, Category.weekly_target_minutes)
    )

    # Planned minutes per category this week
    planned_stmt = (
        select(
            Category.id,
            func.coalesce(func.sum(TimeBlock.planned_duration), 0).label("planned_minutes"),
        )
        .join(TimeBlock, TimeBlock.category_id == Category.id, isouter=True)
        .where(
            and_(
                TimeBlock.date >= week_start,
                TimeBlock.date <= week_end,
            )
        )
        .group_by(Category.id)
    )

    done_rows = (await db.execute(done_stmt)).all()
    planned_rows = {row.id: row.planned_minutes for row in (await db.execute(planned_stmt)).all()}

    categories = []
    total_actual = 0
    total_planned = 0

    for row in done_rows:
        actual = row.actual_minutes or 0
        planned = planned_rows.get(row.id, 0)
        deficit = max(0, row.weekly_target_minutes - actual)
        completion = (actual / row.weekly_target_minutes * 100) if row.weekly_target_minutes > 0 else 0.0

        categories.append(CategoryWeeklyProgress(
            category_id=str(row.id),
            category_name=row.name,
            color_hex=row.color_hex,
            weekly_target_minutes=row.weekly_target_minutes,
            actual_minutes=actual,
            planned_minutes=planned,
            deficit_minutes=deficit,
            completion_pct=round(completion, 1),
        ))
        total_actual += actual
        total_planned += planned

    return WeeklyProgressRead(
        week_start=week_start,
        week_end=week_end,
        categories=categories,
        total_actual_minutes=total_actual,
        total_planned_minutes=total_planned,
    )


async def get_best_hours(db: AsyncSession, days: int = 30) -> BestHoursRead:
    """Compute average productive minutes per hour-of-day over the past N days."""
    cutoff = date.today() - timedelta(days=days)

    stmt = (
        select(
            func.extract("hour", TimeLog.actual_start).label("hour"),
            func.count(TimeLog.id).label("count"),
            func.sum(TimeLog.actual_duration).label("total_minutes"),
        )
        .where(
            and_(
                TimeLog.actual_start >= cutoff,
                TimeLog.actual_end.isnot(None),
                TimeLog.actual_duration.isnot(None),
            )
        )
        .group_by(func.extract("hour", TimeLog.actual_start))
        .order_by(func.extract("hour", TimeLog.actual_start))
    )
    rows = (await db.execute(stmt)).all()

    hours = [
        HourBucket(
            hour=int(row.hour),
            avg_minutes=round((row.total_minutes or 0) / max(row.count, 1), 1),
            sample_count=row.count,
        )
        for row in rows
    ]
    return BestHoursRead(hours=hours)


async def get_deep_work_trend(db: AsyncSession, days: int = 14) -> DeepWorkTrendRead:
    cutoff = date.today() - timedelta(days=days)

    stmt = (
        select(
            TimeBlock.date,
            Category.is_deep_work,
            func.sum(TimeBlock.planned_duration).label("minutes"),
        )
        .join(Category, TimeBlock.category_id == Category.id)
        .where(
            and_(
                TimeBlock.date >= cutoff,
                TimeBlock.status == BlockStatus.done,
            )
        )
        .group_by(TimeBlock.date, Category.is_deep_work)
        .order_by(TimeBlock.date)
    )
    rows = (await db.execute(stmt)).all()

    by_date: dict[date, dict] = defaultdict(lambda: {"deep": 0, "total": 0})
    for row in rows:
        by_date[row.date]["total"] += row.minutes or 0
        if row.is_deep_work:
            by_date[row.date]["deep"] += row.minutes or 0

    day_list = [
        DeepWorkDay(date=d, deep_work_minutes=v["deep"], total_minutes=v["total"])
        for d, v in sorted(by_date.items())
    ]

    avg = round(sum(d.deep_work_minutes for d in day_list) / max(len(day_list), 1), 1)
    mx = max((d.deep_work_minutes for d in day_list), default=0)

    return DeepWorkTrendRead(days=day_list, avg_deep_work_minutes=avg, max_deep_work_minutes=mx)
