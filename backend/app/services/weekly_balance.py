"""Weekly balance service — compute deficits/surplus and category inputs for scheduler."""
from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.time_block import TimeBlock
from app.enums import BlockStatus
from app.services.scheduler import CategoryInput


async def build_category_inputs(
    db: AsyncSession,
    target_date: date,
) -> tuple[list[CategoryInput], int]:
    """
    Build CategoryInput list for the scheduler from current DB state.

    Returns (category_inputs, days_remaining_in_week).
    Days remaining: count of days from target_date to end of that ISO week (Sunday).
    """
    # ISO week: Monday=0 ... Sunday=6
    week_day = target_date.weekday()  # Monday=0
    days_remaining = 7 - week_day

    week_start = target_date - timedelta(days=week_day)
    week_end = week_start + timedelta(days=6)

    # Active categories
    cats_stmt = select(Category).where(Category.is_active == True)
    cats = (await db.execute(cats_stmt)).scalars().all()

    # Actual done minutes this week per category
    done_stmt = (
        select(
            TimeBlock.category_id,
            func.coalesce(func.sum(TimeBlock.planned_duration), 0).label("done_minutes"),
        )
        .where(
            and_(
                TimeBlock.date >= week_start,
                TimeBlock.date < target_date,  # only days before today
                TimeBlock.status == BlockStatus.done,
            )
        )
        .group_by(TimeBlock.category_id)
    )
    done_map = {
        row.category_id: row.done_minutes
        for row in (await db.execute(done_stmt)).all()
    }

    # Missed blocks yesterday
    yesterday = target_date - timedelta(days=1)
    missed_stmt = (
        select(TimeBlock.category_id)
        .where(
            and_(
                TimeBlock.date == yesterday,
                TimeBlock.status == BlockStatus.missed,
            )
        )
        .distinct()
    )
    missed_cats = {row.category_id for row in (await db.execute(missed_stmt)).all()}

    inputs = [
        CategoryInput(
            id=str(cat.id),
            name=cat.name,
            color_hex=cat.color_hex,
            priority_weight=cat.priority_weight,
            weekly_target_minutes=cat.weekly_target_minutes,
            daily_cap_minutes=cat.daily_cap_minutes,
            is_deep_work=cat.is_deep_work,
            actual_this_week=done_map.get(cat.id, 0),
            missed_yesterday=cat.id in missed_cats,
        )
        for cat in cats
    ]

    return inputs, days_remaining
