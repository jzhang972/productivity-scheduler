from datetime import date
from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select
from app.dependencies import DB
from app.models.daily_review import DailyReview
from app.schemas.daily_review import DailyReviewCreate, DailyReviewUpdate, DailyReviewRead

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/", response_model=list[DailyReviewRead])
async def list_reviews(db: DB, limit: int = Query(default=30, ge=1, le=90)):
    stmt = select(DailyReview).order_by(DailyReview.date.desc()).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/by-date", response_model=DailyReviewRead)
async def get_review_by_date(db: DB, date: date = Query(...)):
    stmt = select(DailyReview).where(DailyReview.date == date)
    review = (await db.execute(stmt)).scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found for this date.")
    return review


@router.post("/", response_model=DailyReviewRead, status_code=status.HTTP_201_CREATED)
async def create_review(data: DailyReviewCreate, db: DB):
    existing = (
        await db.execute(select(DailyReview).where(DailyReview.date == data.date))
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=409, detail=f"Review for {data.date} already exists. Use PUT to update."
        )
    review = DailyReview(**data.model_dump())
    db.add(review)
    await db.flush()
    await db.refresh(review)
    return review


@router.put("/{review_id}", response_model=DailyReviewRead)
async def update_review(review_id: str, data: DailyReviewUpdate, db: DB):
    review = await db.get(DailyReview, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found.")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(review, field, value)
    await db.flush()
    await db.refresh(review)
    return review
