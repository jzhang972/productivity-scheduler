# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Backend (run from `backend/`)
```bash
# Install dependencies
pip install -r requirements.txt

# Run the API server (requires Postgres)
uvicorn app.main:app --reload

# Run all tests (no database required — scheduler tests are pure Python)
pytest tests/

# Run a single test file
pytest tests/test_scheduler.py -v

# Run a single test by name
pytest tests/test_scheduler.py::TestSchedulerCaps::test_research_daily_cap_respected -v

# Database migrations
alembic upgrade head
alembic revision --autogenerate -m "description"

# Start Postgres via Docker (from repo root)
docker-compose up db -d
```

### Frontend (run from `frontend/`)
```bash
npm install
npm run dev       # dev server at localhost:3000
npm run build
npm run lint
```

### Standalone UI
Open `scheduler.html` directly in a browser — no build step. Connects to the backend at `http://localhost:8000` (configurable in the UI).

### Git & GitHub
Commit and push to GitHub regularly after completing any meaningful unit of work — do not accumulate large batches of uncommitted changes.

```bash
git add <specific files>
git commit -m "short description of what changed and why"
git push
```

- Prefer specific file staging over `git add .`
- Commit messages should be lowercase, imperative, and describe intent (e.g. `fix scheduler cap overflow`, `add energy rating to review form`)
- Push after every commit — this repo is the source of truth and work should never exist only locally

## Architecture

### Backend (`backend/app/`)

**Entry point**: `main.py` registers all routers and starts the APScheduler nightly job via FastAPI `lifespan`.

**Key design decisions**:
- `database.py` creates the SQLAlchemy async engine **lazily** (not at import time). This lets tests import models and schemas without `asyncpg` installed.
- `enums.py` holds `BlockStatus` as a standalone module with no DB dependencies. Import `BlockStatus` from here, not from `models/time_block.py`, to avoid circular/heavy imports in test contexts.
- `schemas/schedule_types.py` holds `ScheduledBlock` and `ScheduleWarning` as a standalone Pydantic module — also no DB deps. `schemas/schedule.py` re-exports from it. The scheduler service imports from `schedule_types` directly.
- All schema files use `from __future__ import annotations` + `Optional[datetime.date]` (not `date | None`) to avoid field-name shadowing the imported `date` type in Pydantic v2.
- `dependencies.py` exposes `DB = Annotated[AsyncSession, Depends(get_db)]` for use in router function signatures.

**Scheduling algorithm** (`services/scheduler.py`):
- Pure Python, no DB calls — takes `list[CategoryInput]` and returns `(list[ScheduledBlock], list[ScheduleWarning])`.
- Four stages: deficit scoring → slot allocation → block generation → sequencing.
- `CategoryInput` is a dataclass defined in `scheduler.py`; `services/weekly_balance.py` queries the DB and builds `CategoryInput` objects to feed into the scheduler.
- Scheduling constants (work hours, gym slot, deep-work window, caps) all come from `Settings` in `config.py` and can be overridden via `.env`.

**Data flow for schedule generation**:
```
POST /schedule/generate
  → routers/schedule.py
  → weekly_balance.build_category_inputs(db, date)  # reads DB state
  → scheduler.generate_schedule(date, category_inputs, ...)  # pure algorithm
  → writes TimeBlock rows to DB
```

**Nightly job** (`jobs/nightly_schedule.py`): APScheduler cron at 23:00, calls the same `build_category_inputs` + `generate_schedule` pipeline for tomorrow's date.

### Frontend (`frontend/`)

**State split**:
- **Zustand** (`lib/store/`): ephemeral UI state only. `timerStore` tracks the active log ID, block ID, elapsed seconds, and paused state — persisted to `localStorage` so a page refresh doesn't lose a running timer. `uiStore` tracks modal open state and the selected date.
- **React Query** (`lib/hooks/`): all server data. Mutations on `time-blocks` use optimistic updates (`onMutate` / `onError` rollback) for drag-and-drop responsiveness.

**API layer** (`lib/api/`): thin Axios wrappers per resource. `client.ts` sets the base URL from `NEXT_PUBLIC_API_URL`.

**Timeline rendering** (`components/today/Timeline.tsx`): blocks are `position: absolute` inside a fixed-height container. `top = (startMinutes - VIEW_START_MIN) * 1.5px`, `height = duration * 1.5px`. DnD uses `@dnd-kit` with a 15-minute snap grid; drag delta in pixels is converted back to minutes.

**Timer flow**: `useTimer` hook (wraps `timerStore` + API mutations) → calls `POST /time-logs/start` → stores returned `log.id` in Zustand → ticks via `setInterval` → `POST /time-logs/stop` marks block done and clears store.

### Database schema
Four tables: `categories`, `time_blocks`, `time_logs`, `daily_reviews`. The `block_status` PostgreSQL enum (`planned | in_progress | done | missed`) is created by Alembic migration `001_initial_schema.py`. A partial unique index on `time_logs` enforces one open timer per block (`WHERE actual_end IS NULL`).
