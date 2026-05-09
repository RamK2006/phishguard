"""PhishGuard — Application Configuration.

Reads all environment variables using pydantic-settings.
Never hardcode values — everything comes from .env.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    """Central configuration loaded from environment."""

    # ─── Server ───
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    log_level: str = "info"
    debug: bool = False

    # ─── Database ───
    database_url: str = Field(
        default="postgresql+asyncpg://phishguard:phishguard_secret@localhost:5432/phishguard"
    )
    database_url_sync: str = Field(
        default="postgresql://phishguard:phishguard_secret@localhost:5432/phishguard"
    )

    # ─── Redis ───
    redis_url: str = "redis://localhost:6379/0"

    # ─── Qdrant ───
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    # ─── Clerk Auth ───
    clerk_secret_key: str = "REPLACE_WITH_YOUR_KEY"
    clerk_jwks_url: str = "https://your-clerk-instance.clerk.accounts.dev/.well-known/jwks.json"

    # ─── Groq LLM ───
    groq_api_key: str = "REPLACE_WITH_YOUR_KEY"
    groq_model: str = "llama-3.1-70b-versatile"

    # ─── Threat Intelligence ───
    virustotal_api_key: str = "REPLACE_WITH_YOUR_KEY"
    abuseipdb_api_key: str = "REPLACE_WITH_YOUR_KEY"
    urlhaus_api_url: str = "https://urlhaus-api.abuse.ch/v1"

    # ─── Extension ───
    extension_api_key: str = "REPLACE_WITH_YOUR_KEY"

    # ─── Rate Limiting ───
    rate_limit_extension: int = 100
    rate_limit_analyst: int = 1000

    # ─── CORS ───
    cors_origins: str = "http://localhost:3000,http://localhost:3001,chrome-extension://*"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


settings = Settings()
