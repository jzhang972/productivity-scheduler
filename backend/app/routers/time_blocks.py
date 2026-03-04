from datetime import date
from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select, and_
from app.dependencies import DB
from app.models.time_block import TimeBlock
from app.enums import BlockStatus
from app.models.category import Category
from app.schemas.time_block import (
    TimeBlockCreate, TimeBlockUpdate, TimeBlockRead, TimeBlockStatusUpdate
)

router = APIRouter(prefix="/time-blocks", tags=["time-blocks"])


async def _get_or_404(db: DB, block_id: str) -> TimeBlock:
    stmt = select(TimeBlock).where(TimeBlock.id == block_id)
    block = (await db.execute(stmt)).scalar_one_or_none()
    if not block:
        raise HTTPException(status_code=404, detail="Time block not found.")
    return block


@router.get("/", response_model=list[TimeBlockRead])
async def list_blocks_by_date(db: DB, date: date = Query(...)):
    stmt = (
        select(TimeBlock)
        .where(TimeBlock.date == date)
        .order_by(TimeBlock.start_time)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/range", response_model=list[TimeBlockRead])
async def list_blocks_in_range(
    db: DB,
    start: date = Query(...),
    end: date = Query(...),
):
    if end < start:
        raise HTTPException(status_code=400, detail="end must be >= start.")
    stmt = (
        select(TimeBlock)
        .where(and_(TimeBlock.date >= start, TimeBlock.date <= end))
        .order_by(TimeBlock.date, TimeBlock.start_time)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/", response_model=TimeBlockRead, status_code=status.HTTP_201_CREATED)
async def create_block(data: TimeBlockCreate, db: DB):
    cat = await db.get(Category, data.category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found.")

    block = TimeBlock(**data.model_dump())
    db.add(block)
    await db.flush()
    stmt = select(TimeBlock).where(TimeBlock.id == block.id)
    block = (await db.execute(stmt)).scalar_one()
    return block


@router.get("/{block_id}", response_model=TimeBlockRead)
async def get_block(block_id: str, db: DB):
    return await _get_or_404(db, block_id)


@router.put("/{block_id}", response_model=TimeBlockRead)
async def update_block(block_id: str, data: TimeBlockUpdate, db: DB):
    block = await _get_or_404(db, block_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(block, field, value)
    await db.flush()
    stmt = select(TimeBlock).where(TimeBlock.id == block.id)
    return (await db.execute(stmt)).scalar_one()


@router.patch("/{block_id}/status", response_model=TimeBlockRead)
async def update_block_status(block_id: str, data: TimeBlockStatusUpdate, db: DB):
    block = await _get_or_404(db, block_id)
    block.status = data.status
    await db.flush()
    stmt = select(TimeBlock).where(TimeBlock.id == block.id)
    return (await db.execute(stmt)).scalar_one()


@router.delete("/{block_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_block(block_id: str, db: DB):
    block = await _get_or_404(db, block_id)
    await db.delete(block)
