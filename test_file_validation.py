
import pytest

from app.utils.file_validation import validate_file, MAX_FILE_SIZE


JPEG = b"\xff\xd8\xff" + b"\x00" * 20
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 20
PDF = b"%PDF-1.7\n" + b"\x00" * 20


def test_valid_jpeg():
    assert validate_file("photo.jpg", "image/jpeg", JPEG) == ".jpg"


def test_valid_png():
    assert validate_file("photo.png", "image/png", PNG) == ".png"


def test_valid_pdf():
    assert validate_file("document.pdf", "application/pdf", PDF) == ".pdf"


def test_unsupported_extension():
    with pytest.raises(ValueError, match="Unsupported file extension"):
        validate_file("program.exe", "application/octet-stream", b"data")


def test_content_type_mismatch():
    with pytest.raises(ValueError, match="do not match"):
        validate_file("photo.jpg", "image/png", JPEG)


def test_invalid_signature():
    with pytest.raises(ValueError, match="Invalid JPEG"):
        validate_file("photo.jpg", "image/jpeg", b"not a JPEG")


def test_empty_file():
    with pytest.raises(ValueError, match="Empty files"):
        validate_file("photo.jpg", "image/jpeg", b"")


def test_oversized_file():
    with pytest.raises(ValueError, match="5 MB"):
        validate_file(
            "photo.jpg",
            "image/jpeg",
            b"\xff\xd8\xff" + b"\x00" * (MAX_FILE_SIZE - 2),
        )
