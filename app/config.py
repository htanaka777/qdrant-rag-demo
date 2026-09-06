from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str
    openai_model: str = "gpt-5"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536

    qdrant_url: str = "http://qdrant:6333"
    qdrant_collection: str = "company_faq"

    default_top_k: int = 3
    min_score: float = 0.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
