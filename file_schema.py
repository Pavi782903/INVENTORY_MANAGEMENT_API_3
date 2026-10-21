
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FileMetadataResponse(BaseModel):
    id: int
    original_filename: str
    stored_filename: str
    file_path: str
    content_type: str
    file_size: int
    uploaded_at: datetime
    uploaded_by: int | None

    model_config = ConfigDict(from_attributes=True)
