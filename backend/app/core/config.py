import os
from dataclasses import dataclass
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[2]


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


settings = Settings()
