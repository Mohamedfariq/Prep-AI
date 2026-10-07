from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application & Security
    environment: str = "development"
    jwt_secret: str = "change-me-in-env"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7
    frontend_origin: str = "http://localhost:5173"

    # Legacy MongoDB fallback
    mongodb_uri: str = "mongodb://localhost:27017"
    database_name: str = "prepai"

    # PostgreSQL / SQLAlchemy
    database_url: str | None = None

    # Supabase Storage for Resumes
    supabase_url: str | None = None
    supabase_service_role_key: str | None = None
    supabase_bucket_name: str = "resumes"
    supabase_signed_url_expiry_seconds: int = 900

    # Local LLM (Ollama)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"

    # Fallback LLM API (Groq / OpenAI)
    groq_api_key: str | None = None
    openai_api_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=[
            Path(__file__).resolve().parents[2] / ".env",
            Path(__file__).resolve().parents[3] / ".env",
            ".env",
        ],
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def async_database_url(self) -> str:
        if not self.database_url:
            return "sqlite+aiosqlite:///./prepai.db"
        url = self.database_url
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://", 1)
        return url

    @property
    def sync_database_url(self) -> str:
        if not self.database_url:
            return "sqlite:///./prepai.db"
        url = self.database_url
        if url.startswith("postgresql+asyncpg://"):
            return url.replace("postgresql+asyncpg://", "postgresql://", 1)
        return url


@lru_cache
def get_settings() -> Settings:
    return Settings()
