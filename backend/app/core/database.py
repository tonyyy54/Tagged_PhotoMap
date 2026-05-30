from sqlmodel import SQLModel, Session, create_engine

from app.core.config import settings
import app.models  # noqa: F401 - registers SQLModel tables


engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
    if settings.DATABASE_URL.startswith("sqlite")
    else {},
)


def get_session():
    with Session(engine) as session:
        yield session


def create_db():
    SQLModel.metadata.create_all(engine)
