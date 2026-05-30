from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PhotoCreate(BaseModel):
    image_url: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    description: str | None = Field(default=None, max_length=2_000)
    ai_description: str | None = Field(default=None, max_length=2_000)


class PhotoRead(PhotoCreate):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PhotoUpdate(BaseModel):
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    description: str | None = Field(default=None, max_length=2_000)
