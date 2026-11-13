from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "vector-engine-alan-vo"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "127.0.0.1"
    database_url: str = "sqlite+aiosqlite:///./vector_engine.db"

    # CORS
    cors_origins: list[str] = ["http://127.0.0.1:5173", "http://localhost:5173"]

    # LLM (optional, for future phases)
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    llm_base_url: Optional[str] = None
    llm_api_key: Optional[str] = None

    # Auth (future phase)
    oidc_issuer_url: Optional[str] = None
    oidc_client_id: Optional[str] = None
    oidc_client_secret: Optional[str] = None


settings = Settings()