from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select, and_
from app.dependencies import DB
from app.models.time_block import TimeBlock
from app.enums import BlockStatus
from app.models.time_log import TimeLog
from app.schemas.time_log import TimeLogCreate, TimeLogStop, TimeLogUpdate, TimeLogRead

router = APIRouter(prefix="/time-logs", tags=["time-logs"])


@router.post("/start", response_model=TimeLogRead, status_code=status.HTTP_201_CREATED)
async def start_timer(data: TimeLogCreate, db: DB):
    block = await db.get(TimeBlock, data.time_block_id)
    if not block:
        raise HTTPException(status_code=404, detail="Time block not found.")

    open_stmt = select(TimeLog).where(
        and_(TimeLog.time_block_id == data.time_block_id, TimeLog.actual_end == None)
    )
    existing = (await db.execute(open_stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="A timer is already running for this block.")

    block.status = BlockStatus.in_progress

    log = TimeLog(
        time_block_id=data.time_block_id,
        actual_start=datetime.now(timezone.utc),
        notes=data.notes,
    )
    db.add(log)
    await db.flush()
    await db.refresh(log)
    return log


@router.post("/{log_id}/stop", response_model=TimeLogRead)
async def stop_timer(log_id: str, data: TimeLogStop, db: DB):
    log = await db.get(TimeLog, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Time log not found.")
    if log.actual_end is not None:
        raise HTTPException(status_code=409, detail="Timer already stopped.")

    now = datetime.now(timezone.utc)
    # SQLite returns naive datetimes; normalise before arithmetic to avoid TypeError
    actual_start = log.actual_start
    if actual_start.tzinfo is None:
        actual_start = actual_start.replace(tzinfo=timezone.utc)

    log.actual_end = now
    log.actual_duration = max(0, int((now - actual_start).total_seconds() / 60))
    log.interruptions = data.interruptions
    if data.notes:
        log.notes = data.notes

    block = await db.get(TimeBlock, log.time_block_id)
    if block:
        block.status = BlockStatus.done

    await db.flush()
    await db.refresh(log)
    return log


@router.post("/{log_id}/pause", response_model=TimeLogRead)
async def pause_timer(log_id: str, db: DB):
    log = await db.get(TimeLog, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Time log not found.")
    if log.actual_end is not None:
        raise HTTPException(status_code=409, detail="Timer already stopped.")

    now = datetime.now(timezone.utc)
    # SQLite returns naive datetimes; normalise before arithmetic to avoid TypeError
    actual_start = log.actual_start
    if actual_start.tzinfo is None:
        actual_start = actual_start.replace(tzinfo=timezone.utc)

    log.actual_end = now
    log.actual_duration = max(0, int((now - actual_start).total_seconds() / 60))

    await db.flush()
    await db.refresh(log)
    return log


@router.get("/", response_model=list[TimeLogRead])
async def list_logs(db: DB, block_id: str = Query(...)):
    stmt = (
        select(TimeLog)
        .where(TimeLog.time_block_id == block_id)
        .order_by(TimeLog.actual_start.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.put("/{log_id}", response_model=TimeLogRead)
async def update_log(log_id: str, data: TimeLogUpdate, db: DB):
    log = await db.get(TimeLog, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Time log not found.")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(log, field, value)
    await db.flush()
    await db.refresh(log)
    return log
