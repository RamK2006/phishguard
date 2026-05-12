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

    # ─── Upstash Redis ───
    upstash_redis_url: str = ""
    upstash_redis_token: str = ""

    # ─── Clerk Auth ───
    clerk_secret_key: str = ""
    clerk_jwks_url: str = "https://your-clerk-instance.clerk.accounts.dev/.well-known/jwks.json"

    # ─── Google Gemini LLM ───
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    # ─── Threat Intelligence ───
    virustotal_api_key: str = ""
    abuseipdb_api_key: str = ""
    urlhaus_api_url: str = "https://urlhaus-api.abuse.ch/v1"

    # ─── Extension ───
    extension_api_key: str = ""

    # ─── Rate Limiting ───
    rate_limit_extension: int = 100
    rate_limit_analyst: int = 1000

    # ─── CORS ───
    cors_origins: str = "http://localhost:3000,http://localhost:3001,chrome-extension://*,https://*.vercel.app"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


settings = Settings()
