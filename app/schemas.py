from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar("T")

class FileMetadataBase(BaseModel):
    filename: str
    file_path: str

class FileMetadataCreate(FileMetadataBase):
    pass

class FileMetadata(FileMetadataBase):
    id: int

    class Config:
        from_attributes = True

class Response(BaseModel, Generic[T]):
    status_code: int = 200
    error: bool = False
    detail: str
    data: Optional[T] = None