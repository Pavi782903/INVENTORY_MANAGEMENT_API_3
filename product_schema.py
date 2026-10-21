
from pydantic import BaseModel, ConfigDict

from app.schemas.file_schema import FileMetadataResponse


class ProductImageAssociation(BaseModel):
    file_id: int


class ProductResponse(BaseModel):
    id: int
    name: str
    image_file_id: int | None
    image_file: FileMetadataResponse | None = None

    model_config = ConfigDict(from_attributes=True)
