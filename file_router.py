
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_file_access
from app.schemas.file_schema import FileMetadataResponse
from app.services.file_service import FileService
from app.utils.file_validation import MAX_FILE_SIZE

router = APIRouter(
    prefix="/api/v1/files",
    tags=["Files"],
)


@router.post(
    "/upload",
    response_model=FileMetadataResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_file(
    file: UploadFile = File(...),
    category: str = Form(..., description="products or suppliers"),
    db: Session = Depends(get_db),
    user: dict = Depends(require_file_access),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    # Read at most 5 MB plus one byte, so oversized uploads are rejected.
    data = bytearray()
    try:
        while True:
            chunk = file.file.read(64 * 1024)
            if not chunk:
                break
            data.extend(chunk)
            if len(data) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail="File exceeds the maximum size of 5 MB.",
                )
    finally:
        file.file.close()

    if not data:
        raise HTTPException(status_code=400, detail="Empty files are not allowed.")

    return FileService(db).upload(
        filename=file.filename,
        content_type=file.content_type or "",
        data=bytes(data),
        category=category,
        user_id=user["id"],
    )


@router.get("", response_model=list[FileMetadataResponse])
def list_files(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    user: dict = Depends(require_file_access),
):
    return FileService(db).list(user["id"], skip, limit)


@router.get("/{file_id}", response_model=FileMetadataResponse)
def get_file(
    file_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_file_access),
):
    return FileService(db).get(file_id, user["id"])


@router.get("/{file_id}/download")
def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_file_access),
):
    metadata, path = FileService(db).resolve_download_path(
        file_id, user["id"]
    )

    return FileResponse(
        path=path,
        media_type=metadata.content_type,
        filename=Path(metadata.original_filename).name,
        content_disposition_type="attachment",
    )


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_file_access),
):
    FileService(db).delete(file_id, user["id"])
    return None
