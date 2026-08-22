from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "EventScout KZ"
    environment: str = "development"
    database_url: str = "sqlite:///./eventscout.db"
    telegram_bot_token: str | None = None
    telegram_api_id: int | None = None
    telegram_api_hash: str | None = None
    telegram_channels: str = "astanahub,techgarden,jetisudigital"
    scraper_urls: str = "https://astanahub.com/"
    scraper_interval_hours: int = 3
    seed_mock_events: bool = False
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-1.5-flash"
    admin_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
