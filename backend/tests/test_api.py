from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image
from PIL.TiffImagePlugin import IFDRational
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.core.database import get_session
from app.core.config import settings
from main import app
from app.services.exif_service import _to_degrees, extract_gps_coordinates


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def override_get_session():
    with Session(engine) as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


def setup_function():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_tagged_photo_flow():
    with TestClient(app) as client:
        register = client.post(
            "/auth/register",
            json={
                "email": "map@example.com",
                "username": "mapper",
                "password": "correct-horse",
            },
        )
        assert register.status_code == 200

        login = client.post(
            "/auth/login",
            json={"email": "map@example.com", "password": "correct-horse"},
        )
        assert login.status_code == 200
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        upload = client.post(
            "/photos/upload",
            headers=headers,
            data={
                "latitude": "48.8584",
                "longitude": "2.2945",
                "description": "Eiffel Tower",
            },
            files={"image": ("tower.jpg", b"fake-jpeg-for-api-test", "image/jpeg")},
        )
        assert upload.status_code == 200
        photo = upload.json()
        assert photo["latitude"] == 48.8584
        assert photo["image_url"].startswith("/uploads/")
        uploaded_file = settings.UPLOAD_DIR / Path(photo["image_url"]).name
        assert uploaded_file.exists()

        map_photos = client.get(
            "/photos",
            params={"min_lat": 48, "max_lat": 49, "min_lng": 2, "max_lng": 3},
        )
        assert map_photos.status_code == 200
        assert [item["id"] for item in map_photos.json()] == [photo["id"]]

        comment = client.post(
            f"/photos/{photo['id']}/comments",
            headers=headers,
            json={"content": "Great viewpoint"},
        )
        assert comment.status_code == 200

        comments = client.get(f"/photos/{photo['id']}/comments")
        assert comments.status_code == 200
        assert comments.json()[0]["content"] == "Great viewpoint"
        uploaded_file.unlink()


def test_exif_coordinate_conversion():
    assert _to_degrees((48, 51, 30.24)) == 48.8584


def test_extract_gps_coordinates_from_jpeg_exif():
    image = Image.new("RGB", (1, 1))
    exif = Image.Exif()
    rational = IFDRational
    exif[0x8825] = {
        1: "N",
        2: (rational(48), rational(51), rational(3024, 100)),
        3: "E",
        4: (rational(2), rational(21), rational(792, 100)),
    }
    content = BytesIO()
    image.save(content, format="JPEG", exif=exif)

    assert extract_gps_coordinates(content.getvalue()) == (48.8584, 2.3522000000000003)


def test_upload_requires_coordinates_when_image_has_no_gps():
    with TestClient(app) as client:
        client.post(
            "/auth/register",
            json={
                "email": "nogps@example.com",
                "username": "nogps",
                "password": "correct-horse",
            },
        )
        login = client.post(
            "/auth/login",
            json={"email": "nogps@example.com", "password": "correct-horse"},
        )
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        upload = client.post(
            "/photos/upload",
            headers=headers,
            files={"image": ("plain.jpg", b"not-an-image", "image/jpeg")},
        )

    assert upload.status_code == 422
    assert upload.json()["detail"] == (
        "Image has no EXIF GPS data. Enter latitude and longitude manually."
    )


def test_upload_uses_exif_coordinates_when_form_coordinates_are_missing(monkeypatch):
    monkeypatch.setattr(
        "app.routers.photos.extract_gps_coordinates",
        lambda _: (48.8566, 2.3522),
    )
    with TestClient(app) as client:
        client.post(
            "/auth/register",
            json={
                "email": "exif@example.com",
                "username": "exif",
                "password": "correct-horse",
            },
        )
        login = client.post(
            "/auth/login",
            json={"email": "exif@example.com", "password": "correct-horse"},
        )
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        upload = client.post(
            "/photos/upload",
            headers=headers,
            files={"image": ("gps.jpg", b"image-with-gps", "image/jpeg")},
        )

    assert upload.status_code == 200
    photo = upload.json()
    assert photo["latitude"] == 48.8566
    assert photo["longitude"] == 2.3522
    (settings.UPLOAD_DIR / Path(photo["image_url"]).name).unlink()
