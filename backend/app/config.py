from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Engineering Intelligence Platform"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://engineering_app:engineering_app@db:5432/engineering_intelligence"
    data_path: str = "data/generated/platform_data.json"
    llm_provider: str = "ollama"
    llm_model: str = "qwen2.5:7b"
    ollama_base_url: str = "http://host.docker.internal:11434"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    cors_origins: str = "http://localhost:5173"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
