from uuid import UUID
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from app.dependencies import DB
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryRead

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategoryRead])
async def list_categories(db: DB, active_only: bool = False):
    stmt = select(Category)
    if active_only:
        stmt = stmt.where(Category.is_active == True)
    stmt = stmt.order_by(Category.priority_weight.desc(), Category.name)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(data: CategoryCreate, db: DB):
    existing = await db.execute(select(Category).where(Category.name == data.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"Category '{data.name}' already exists.")
    cat = Category(**data.model_dump())
    db.add(cat)
    await db.flush()
    await db.refresh(cat)
    return cat


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(category_id: UUID, db: DB):
    cat = await db.get(Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found.")
    return cat


@router.put("/{category_id}", response_model=CategoryRead)
async def update_category(category_id: UUID, data: CategoryUpdate, db: DB):
    cat = await db.get(Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found.")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(cat, field, value)
    await db.flush()
    await db.refresh(cat)
    return cat


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: UUID, db: DB):
    cat = await db.get(Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found.")
    await db.delete(cat)
