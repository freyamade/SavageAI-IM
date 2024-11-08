from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class _Settings(BaseSettings):
    DISCORD_TOKEN: str
    SENTRY_DSN: str | None = None


Settings = _Settings()
