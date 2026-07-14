from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """환경변수(.env)를 읽어오는 설정 클래스."""

    DATABASE_URL: str = "sqlite:///./localhub.db"
    CORS_ORIGINS: str = "http://localhost:5173"
    OPENAI_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        """콤마로 구분된 CORS_ORIGINS 문자열을 리스트로 변환."""
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
