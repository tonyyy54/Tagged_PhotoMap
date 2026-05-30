from sqlmodel import Session, select

from app.models.comments import Comment
from app.models.photo import Photo
from app.models.user import User
from app.schemas.comments import CommentCreate


def create_comment(
    photo_id: int,
    comment_create: CommentCreate,
    current_user: User,
    session: Session
):

    photo = session.get(
        Photo,
        photo_id
    )

    if not photo:
        raise ValueError(
            "Photo not found"
        )

    comment = Comment(
        photo_id=photo_id,
        user_id=current_user.id,
        content=comment_create.content
    )

    session.add(comment)
    session.commit()
    session.refresh(comment)

    return comment


def get_comments_by_photo(
    photo_id: int,
    session: Session
):

    photo = session.get(
        Photo,
        photo_id
    )

    if not photo:
        raise ValueError(
            "Photo not found"
        )

    comments = session.exec(
        select(Comment).where(
            Comment.photo_id == photo_id
        )
    ).all()

    return comments