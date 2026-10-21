
import os
import uuid
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import FileMetadata
from app.repositories.file_repository import FileRepository
from app.utils.file_validation import validate_file, MAX_FILE_SIZE

BASE_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = (BASE_DIR / os.getenv("UPLOAD_DIR", "uploads")).resolve()

FOLDERS = {
    "products": UPLOAD_DIR / "products",
    "suppliers": UPLOAD_DIR / "suppliers",
}


def prepare_storage() -> None:
    for folder in FOLDERS.values():
        folder.mkdir(parents=True, exist_ok=True)


class FileService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = FileRepository(db)

    def upload(
        self,
        filename: str,
        content_type: str,
        data: bytes,
        category: str,
        user_id: int,
    ) -> FileMetadata:
        if category not in FOLDERS:
            raise HTTPException(
                status_code=400,
                detail="Category must be products or suppliers.",
            )

        try:
            extension = validate_file(filename, content_type, data)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

        # Only the final extension is used; never use a client path.
        safe_name = f"{uuid.uuid4().hex}{extension}"
        target_dir = FOLDERS[category]
        target_path = (target_dir / safe_name).resolve()

        if not target_path.is_relative_to(target_dir.resolve()):
            raise HTTPException(status_code=400, detail="Invalid file path.")

        relative_path = target_path.relative_to(UPLOAD_DIR).as_posix()
        created_file = False

        try:
            prepare_storage()

            # Exclusive creation prevents overwriting an existing file.
            with target_path.open("xb") as output:
                created_file = True
                output.write(data)

            metadata = FileMetadata(
                original_filename=Path(filename).name[:255],
                stored_filename=safe_name,
                file_path=relative_path,
                content_type=content_type,
                file_size=len(data),
                uploaded_by=user_id,
            )

            self.repo.create(metadata)
            self.db.commit()
            self.db.refresh(metadata)
            return metadata

        except HTTPException:
            self.db.rollback()
            if created_file:
                target_path.unlink(missing_ok=True)
            raise

        except (OSError, SQLAlchemyError) as exc:
            self.db.rollback()
            if created_file:
                target_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=500,
                detail="Upload failed. No file metadata was committed.",
            ) from exc

    def get(self, file_id: int, user_id: int) -> FileMetadata:
        metadata = self.repo.get(file_id)
        if metadata is None:
            raise HTTPException(status_code=404, detail="File not found.")

        if metadata.uploaded_by != user_id:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to access this file.",
            )

        return metadata

    def list(self, user_id: int, skip: int = 0, limit: int = 100):
        # List only the current user's files.
        return (
            self.db.query(FileMetadata)
            .filter(FileMetadata.uploaded_by == user_id)
            .order_by(FileMetadata.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def resolve_download_path(
        self, file_id: int, user_id: int
    ) -> tuple[FileMetadata, Path]:
        metadata = self.get(file_id, user_id)

        path = (UPLOAD_DIR / metadata.file_path).resolve()
        if not path.is_relative_to(UPLOAD_DIR):
            raise HTTPException(status_code=400, detail="Invalid storage path.")

        if not path.is_file():
            raise HTTPException(
                status_code=404,
                detail="The file is missing from storage.",
            )

        return metadata, path

    def delete(self, file_id: int, user_id: int) -> None:
        metadata = self.get(file_id, user_id)

        # Never delete a file still referenced by a product.
        if metadata.products:
            raise HTTPException(
                status_code=409,
                detail="This file is associated with a product. "
                       "Remove the association before deleting it.",
            )

        path = (UPLOAD_DIR / metadata.file_path).resolve()
        if not path.is_relative_to(UPLOAD_DIR):
            raise HTTPException(status_code=400, detail="Invalid storage path.")

        # Keep the physical file recoverable until the DB commit succeeds.
        backup = None
        try:
            if path.exists():
                backup = path.with_name(
                    f".{path.name}.{uuid.uuid4().hex}.deleting"
                )
                path.replace(backup)

            self.repo.delete(metadata)
            self.db.commit()

            if backup is not None:
                backup.unlink(missing_ok=True)

        except (OSError, SQLAlchemyError) as exc:
            self.db.rollback()
            if backup is not None and backup.exists():
                backup.replace(path)
            raise HTTPException(
                status_code=500,
                detail="Deletion failed; the operation was rolled back.",
            ) from exc
