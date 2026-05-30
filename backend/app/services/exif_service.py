from io import BytesIO

from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import GPSTAGS


def _to_degrees(value) -> float:
    degrees, minutes, seconds = value
    return float(degrees) + float(minutes) / 60 + float(seconds) / 3600


def extract_gps_coordinates(content: bytes) -> tuple[float, float] | None:
    try:
        with Image.open(BytesIO(content)) as image:
            exif = image.getexif()
            gps_ifd = exif.get_ifd(0x8825)
    except (OSError, UnidentifiedImageError, ValueError):
        return None

    gps = {
        GPSTAGS.get(tag, tag): value
        for tag, value in gps_ifd.items()
    }
    latitude = gps.get("GPSLatitude")
    longitude = gps.get("GPSLongitude")
    if not latitude or not longitude:
        return None

    latitude_value = _to_degrees(latitude)
    longitude_value = _to_degrees(longitude)
    if gps.get("GPSLatitudeRef") == "S":
        latitude_value *= -1
    if gps.get("GPSLongitudeRef") == "W":
        longitude_value *= -1
    return latitude_value, longitude_value
