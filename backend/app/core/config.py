"""Application settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RISKLAB_", env_file=".env", extra="ignore")

    app_name: str = "RiskLab"
    cache_dir: str = ".cache/risklab"
    cache_ttl_seconds: int = 86400
    risk_free_fallback: float = 0.045
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    market_benchmark: str = "^GSPC"
    tnx_ticker: str = "^TNX"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
