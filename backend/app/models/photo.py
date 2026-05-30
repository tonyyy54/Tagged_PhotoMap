from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class Photo(SQLModel, table=True):
    __tablename__ = "photos"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    image_url: str
    latitude: float
    longitude: float
    description: str | None = None
    ai_description: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
