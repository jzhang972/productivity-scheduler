from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.jobs.nightly_schedule import create_scheduler
from app.routers import categories, time_blocks, time_logs, daily_review, analytics, schedule

UI_FILE = Path(__file__).parents[2] / "scheduler.html"

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = create_scheduler()
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(
    title="Personal Productivity Scheduler API",
    version="1.0.0",
    description="Schedule, track, and optimize your deep work sessions.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.vercel.app", "null"],
    allow_origin_regex=r"https?://localhost(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(categories.router)
app.include_router(time_blocks.router)
app.include_router(time_logs.router)
app.include_router(daily_review.router)
app.include_router(analytics.router)
app.include_router(schedule.router)


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
async def serve_ui():
    return FileResponse(UI_FILE)
