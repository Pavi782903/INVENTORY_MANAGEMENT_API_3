
from pathlib import Path

MAX_FILE_SIZE = 5 * 1024 * 1024

ALLOWED_TYPES = {
    ".jpg": ("image/jpeg",),
    ".jpeg": ("image/jpeg",),
    ".png": ("image/png",),
    ".pdf": ("application/pdf",),
}


def validate_file(filename: str, content_type: str, data: bytes) -> str:
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_TYPES:
        raise ValueError("Unsupported file extension. Allowed: JPG, PNG, PDF.")

    if content_type not in ALLOWED_TYPES[extension]:
        raise ValueError("File extension and content type do not match.")

    if not data:
        raise ValueError("Empty files are not allowed.")

    if len(data) > MAX_FILE_SIZE:
        raise ValueError("File exceeds the 5 MB limit.")

    if extension in (".jpg", ".jpeg"):
        if not data.startswith(b"\xff\xd8\xff"):
            raise ValueError("Invalid JPEG file content.")

    elif extension == ".png":
        if not data.startswith(b"\x89PNG\r\n\x1a\n"):
            raise ValueError("Invalid PNG file content.")

    elif extension == ".pdf":
        if not data.startswith(b"%PDF-"):
            raise ValueError("Invalid PDF file content.")

    return extension
