from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/scheduler"
    database_url_sync: str = "postgresql://postgres:password@localhost:5432/scheduler"
    secret_key: str = "change-me-in-production-very-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # Scheduling defaults
    work_start_hour: int = 7  # 07:00
    work_end_hour: int = 22   # 22:00 (7am + 15h window, 9h work + buffers)
    work_minutes_per_day: int = 540  # 9 hours
    min_block_minutes: int = 45
    buffer_minutes: int = 15
    gym_start_hour: int = 12
    gym_end_hour: int = 13
    deep_work_window_start: int = 7   # 07:00
    deep_work_window_end: int = 11    # 11:00
    research_daily_cap_minutes: int = 240

    model_config = {"env_file": ".env"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
