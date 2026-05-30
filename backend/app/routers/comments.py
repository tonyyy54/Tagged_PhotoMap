from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.core.database import get_session
from app.models.comments import Comment
from app.models.photo import Photo
from app.models.user import User
from app.schemas.comments import CommentCreate, CommentRead
from app.core.security import get_current_user

router = APIRouter(prefix="/photos", tags=["Comments"])


@router.post("/{photo_id}/comments", response_model=CommentRead)
def create_comment(
    photo_id: int,
    comment_create: CommentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    photo = session.get(Photo, photo_id)

    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    comment = Comment(
        photo_id=photo_id,
        user_id=current_user.id,
        content=comment_create.content
    )

    session.add(comment)
    session.commit()
    session.refresh(comment)

    return comment


@router.get("/{photo_id}/comments", response_model=list[CommentRead])
def get_comments(
    photo_id: int,
    session: Session = Depends(get_session)
):
    photo = session.get(Photo, photo_id)

    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    comments = session.exec(
        select(Comment).where(Comment.photo_id == photo_id)
    ).all()

    return comments