import os
from pydantic import BaseModel
from dotenv import load_dotenv

# Load .env when available
load_dotenv()


class Settings(BaseModel):
    """Application settings loaded from environment variables."""
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    CORS_ALLOW_ORIGINS: list[str] = (
        os.getenv("CORS_ALLOW_ORIGINS", "*").split(",") if os.getenv("CORS_ALLOW_ORIGINS") else ["*"]
    )
    # Placeholder for potential database integration
    DATABASE_URL: str | None = os.getenv("DATABASE_URL")


settings = Settings()
