import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import dotenv_values


BACKEND_DIR = Path(__file__).resolve().parents[2]
DOTENV = dotenv_values(BACKEND_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{(BACKEND_DIR / 'tagged_photos.db').as_posix()}",
    )
    SECRET_KEY: str = os.getenv("SECRET_KEY", "development-only-change-me")
    UPLOAD_DIR: Path = Path(
        os.getenv("UPLOAD_DIR", str(BACKEND_DIR / "uploads"))
    )
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY") or DOTENV.get("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL") or DOTENV.get("OPENAI_MODEL", "gpt-5.4-mini")
    OPENAI_TIMEOUT_SECONDS: float = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "15"))


settings = Settings()
