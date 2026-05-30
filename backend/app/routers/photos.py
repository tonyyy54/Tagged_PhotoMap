from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlmodel import Session, select

from app.core.config import settings
from app.core.database import get_session
from app.core.security import get_current_user
from app.models.photo import Photo
from app.models.user import User
from app.schemas.photo import PhotoCreate, PhotoRead
from app.services.exif_service import extract_gps_coordinates

router = APIRouter(prefix="/photos", tags=["Photos"])
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


def _validate_coordinates(latitude: float, longitude: float) -> None:
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise HTTPException(status_code=422, detail="Invalid coordinates")


@router.post("", response_model=PhotoRead)
def create_photo_from_url(
    photo_create: PhotoCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    photo = Photo(user_id=current_user.id, **photo_create.model_dump())
    session.add(photo)
    session.commit()
    session.refresh(photo)
    return photo


@router.post("/upload", response_model=PhotoRead)
async def upload_photo(
    image: UploadFile = File(...),
    latitude: float | None = Form(default=None),
    longitude: float | None = Form(default=None),
    description: str | None = Form(default=None),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=415, detail="Unsupported image type")

    content = await image.read()
    if latitude is None or longitude is None:
        coordinates = extract_gps_coordinates(content)
        if coordinates is None:
            raise HTTPException(
                status_code=422,
                detail="Image has no EXIF GPS data. Enter latitude and longitude manually.",
            )
        latitude, longitude = coordinates
    _validate_coordinates(latitude, longitude)

    suffix = Path(image.filename or "").suffix.lower()
    suffix = suffix if suffix in {".jpg", ".jpeg", ".png", ".webp"} else ".jpg"
    filename = f"{uuid4().hex}{suffix}"
    (settings.UPLOAD_DIR / filename).write_bytes(content)

    photo = Photo(
        user_id=current_user.id,
        image_url=f"/uploads/{filename}",
        latitude=latitude,
        longitude=longitude,
        description=description,
    )
    session.add(photo)
    session.commit()
    session.refresh(photo)
    return photo


@router.get("", response_model=list[PhotoRead])
def get_photos(
    min_lat: float | None = None,
    max_lat: float | None = None,
    min_lng: float | None = None,
    max_lng: float | None = None,
    limit: int = 500,
    session: Session = Depends(get_session),
):
    limit = min(max(limit, 1), 1_000)
    statement = select(Photo)
    if min_lat is not None:
        statement = statement.where(Photo.latitude >= min_lat)
    if max_lat is not None:
        statement = statement.where(Photo.latitude <= max_lat)
    if min_lng is not None:
        statement = statement.where(Photo.longitude >= min_lng)
    if max_lng is not None:
        statement = statement.where(Photo.longitude <= max_lng)
    return session.exec(statement.limit(limit)).all()
