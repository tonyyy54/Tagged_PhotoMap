from sqlmodel import Session, select

from app.models.photo import Photo
from app.models.user import User
from app.schemas.photo import PhotoCreate


def create_photo(
    photo_create: PhotoCreate,
    current_user: User,
    session: Session
) -> Photo:

    photo = Photo(
        user_id=current_user.id,
        image_url=photo_create.image_url,
        latitude=photo_create.latitude,
        longitude=photo_create.longitude,
        description=photo_create.description,
        ai_description=photo_create.ai_description
    )

    session.add(photo)
    session.commit()
    session.refresh(photo)

    return photo


def get_all_photos(
    session: Session
):

    photos = session.exec(
        select(Photo)
    ).all()

    return photos


def get_photo_by_id(
    photo_id: int,
    session: Session
):

    return session.get(
        Photo,
        photo_id
    )