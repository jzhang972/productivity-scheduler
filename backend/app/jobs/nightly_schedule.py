"""
Nightly APScheduler job — runs at 23:00 to generate tomorrow's schedule.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import date, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select, and_

from app.database import _get_session_factory
from app.models.time_block import TimeBlock
from app.enums import BlockStatus
from app.services.scheduler import generate_schedule
from app.services.weekly_balance import build_category_inputs

logger = logging.getLogger(__name__)


async def _generate_tomorrow() -> None:
    tomorrow = date.today() + timedelta(days=1)
    logger.info(f"Nightly scheduler: generating schedule for {tomorrow}")

    async with _get_session_factory()() as db:
        try:
            # Remove existing planned blocks for tomorrow if any
            existing_stmt = select(TimeBlock).where(
                and_(
                    TimeBlock.date == tomorrow,
                    TimeBlock.status == BlockStatus.planned,
                )
            )
            existing = (await db.execute(existing_stmt)).scalars().all()
            for b in existing:
                await db.delete(b)
            await db.flush()

            # Build inputs and generate
            category_inputs, days_remaining = await build_category_inputs(db, tomorrow)
            blocks, warnings = generate_schedule(
                target_date=tomorrow,
                categories=category_inputs,
                days_remaining_in_week=days_remaining,
                include_gym=True,
            )

            for b in blocks:
                tb = TimeBlock(
                    category_id=b.category_id,
                    date=b.date,
                    start_time=b.start_time,
                    end_time=b.end_time,
                    planned_duration=b.planned_duration,
                    title=b.title,
                    status=BlockStatus.planned,
                )
                db.add(tb)

            await db.commit()
            logger.info(
                f"Nightly scheduler: created {len(blocks)} blocks for {tomorrow}. "
                f"Warnings: {[w.code for w in warnings]}"
            )
        except Exception:
            await db.rollback()
            logger.exception("Nightly scheduler job failed.")


def create_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        _generate_tomorrow,
        trigger=CronTrigger(hour=23, minute=0),
        id="nightly_schedule",
        replace_existing=True,
        misfire_grace_time=3600,
    )
    return scheduler
