"""Schedule router — trigger schedule generation and preview results."""
from datetime import date, datetime, timezone
from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select, and_

from app.dependencies import DB
from app.models.time_block import TimeBlock
from app.enums import BlockStatus
from app.models.category import Category
from app.schemas.schedule import (
    ScheduleGenerateRequest,
    SchedulePreviewResponse,
    ScheduledBlock,
)
from app.services.scheduler import generate_schedule, CategoryInput
from app.services.weekly_balance import build_category_inputs

router = APIRouter(prefix="/schedule", tags=["schedule"])


@router.post("/generate", response_model=SchedulePreviewResponse, status_code=status.HTTP_201_CREATED)
async def generate_schedule_endpoint(data: ScheduleGenerateRequest, db: DB):
    """
    Generate and persist a schedule for target_date.
    If force_regenerate=True, existing planned blocks for that date are deleted first.
    """
    target = data.target_date

    # Handle existing blocks
    existing_stmt = select(TimeBlock).where(
        and_(
            TimeBlock.date == target,
            TimeBlock.status == BlockStatus.planned,
        )
    )
    existing = (await db.execute(existing_stmt)).scalars().all()

    if existing and not data.force_regenerate:
        raise HTTPException(
            status_code=409,
            detail=f"Schedule for {target} already has {len(existing)} planned blocks. "
                   "Use force_regenerate=true to overwrite.",
        )

    if data.force_regenerate:
        for block in existing:
            await db.delete(block)
        await db.flush()

    # Build category inputs from DB state
    category_inputs, days_remaining = await build_category_inputs(db, target)

    # Run scheduling algorithm
    blocks, warnings = generate_schedule(
        target_date=target,
        categories=category_inputs,
        days_remaining_in_week=days_remaining,
        include_gym=True,
    )

    # Persist generated blocks
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

    await db.flush()

    return SchedulePreviewResponse(
        target_date=target,
        blocks=blocks,
        total_planned_minutes=sum(b.planned_duration for b in blocks),
        warnings=warnings,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/preview", response_model=SchedulePreviewResponse)
async def preview_schedule(
    db: DB,
    date: date = Query(...),
):
    """
    Preview what a generated schedule would look like WITHOUT persisting.
    """
    category_inputs, days_remaining = await build_category_inputs(db, date)
    blocks, warnings = generate_schedule(
        target_date=date,
        categories=category_inputs,
        days_remaining_in_week=days_remaining,
        include_gym=True,
    )

    return SchedulePreviewResponse(
        target_date=date,
        blocks=blocks,
        total_planned_minutes=sum(b.planned_duration for b in blocks),
        warnings=warnings,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
