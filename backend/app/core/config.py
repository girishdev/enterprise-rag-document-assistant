from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Enterprise RAG Document Assistant"
    api_v1_prefix: str = "/api/v1"

    database_url: str

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    openai_api_key: str
    openai_model: str = "gpt-5.6"

    chat_system_prompt: str = (
        "You are a helpful enterprise AI assistant. "
        "Answer clearly and concisely."
    )

    chat_temperature: float = 0.2
    chat_max_output_tokens: int = 1000

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()