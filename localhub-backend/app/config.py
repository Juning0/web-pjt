from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    """환경변수(.env)를 읽어오는 설정 클래스."""

    DATABASE_URL: str = "sqlite:///./localhub.db"
    CORS_ORIGINS: str = (
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:5174,http://127.0.0.1:5174"
    )
    OPENAI_API_KEY: str = ""
    
    CHAT_RATE_LIMIT_ENABLED: bool = True
    CHAT_RATE_LIMIT_REQUESTS: int = 5
    CHAT_RATE_LIMIT_WINDOW_SECONDS: int = 60
    CHAT_DAILY_LIMIT_PER_CLIENT: int = 50
    CHAT_DAILY_LIMIT_GLOBAL: int = 200

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        """콤마로 구분된 CORS_ORIGINS 문자열을 리스트로 변환."""
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
