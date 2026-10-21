
from sqlalchemy.orm import Session

from app.models import FileMetadata


class FileRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, metadata: FileMetadata) -> FileMetadata:
        self.db.add(metadata)
        self.db.flush()
        return metadata

    def get(self, file_id: int) -> FileMetadata | None:
        return (
            self.db.query(FileMetadata)
            .filter(FileMetadata.id == file_id)
            .first()
        )

    def list(self, skip: int = 0, limit: int = 100):
        return (
            self.db.query(FileMetadata)
            .order_by(FileMetadata.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def delete(self, metadata: FileMetadata) -> None:
        self.db.delete(metadata)
        self.db.flush()
