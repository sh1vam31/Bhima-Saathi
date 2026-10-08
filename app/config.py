from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    LLM_PROVIDER: str = "groq"
    LLM_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    PROMPT_VERSION: str = "v1"
    WHATSAPP_AUTH_TOKEN: str = "test_token"
    RZP_KEY_ID: str = "test_key_id"
    RZP_KEY_SECRET: str = "test_key_secret"
    RZP_WEBHOOK_SECRET: str = "test_webhook_secret"
    DATABASE_URL: str = "sqlite:///./bima_saathi.db"
    MOCK_BASE_URL: str = "http://localhost:8100"
    ADMIN_API_KEY: str = "admin_secret"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
