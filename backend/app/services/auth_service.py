from sqlmodel import Session, select

from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)


def register_user(
    user_create: UserCreate,
    session: Session
) -> User:

    existing_user = session.exec(
        select(User).where(
            User.email == user_create.email
        )
    ).first()

    if existing_user:
        raise ValueError("Email already exists")

    user = User(
        email=user_create.email,
        username=user_create.username,
        password_hash=hash_password(
            user_create.password
        )
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


def login_user(
    user_login: UserLogin,
    session: Session
):

    user = session.exec(
        select(User).where(
            User.email == user_login.email
        )
    ).first()

    if not user:
        raise ValueError("Invalid credentials")

    if not verify_password(
        user_login.password,
        user.password_hash
    ):
        raise ValueError("Invalid credentials")

    token = create_access_token(
        {"sub": str(user.id)}
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }