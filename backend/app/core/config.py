from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

# Define a Settings class that inherits from BaseSettings to manage application configuration
# The Settings class includes various configuration parameters such as app name, API prefix, database URL, secret key, algorithm, token expiration time, OpenAI API key, model, chat system prompt, temperature, and maximum output tokens.
# The model_config attribute specifies that the settings should be loaded from a .env file and that any extra fields in the environment should be ignored.
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

# about lru_cache: https://docs.python.org/3/library/functools.html#functools.lru_cache
@lru_cache
# The get_settings function is decorated with lru_cache to cache the settings for performance optimization. It returns an instance of the Settings class, which loads the configuration from the .env file.
def get_settings() -> Settings:
    return Settings()