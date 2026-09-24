from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    canonical_timezone: str = "UTC"
    request_timeout: int = 30
    max_retries: int = 3
    rate_limit_calls_per_minute: int = 5
    redis_url: str | None = None
    cache_ttl_seconds: int = 300
    relative_volume_lookback_days: int = 20

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()  # type: ignore[call-arg]
