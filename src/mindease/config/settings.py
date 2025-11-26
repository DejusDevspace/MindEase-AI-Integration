from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    MAX_TOKENS: int = 500
    TEMPERATURE: float = 0.7
    DEBUG: bool = False


settings = Settings()
