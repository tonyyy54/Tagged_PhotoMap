from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.core.database import get_session
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserLogin
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserRead)
def register(user_create: UserCreate, session: Session = Depends(get_session)):
    existing_user = session.exec(
        select(User).where(
            (User.email == user_create.email) | (User.username == user_create.username)
        )
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email or username already registered")

    user = User(
        email=user_create.email,
        username=user_create.username,
        password_hash=hash_password(user_create.password)
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user

@router.post("/login")
def login(user_login: UserLogin, session: Session = Depends(get_session)):
    user = session.exec(
        select(User).where(User.email == user_login.email)
    ).first()

    if not user or not verify_password(user_login.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})

    return {
        "access_token": token,
        "token_type": "bearer"
    }
