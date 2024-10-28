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
        orm_mode: True

class Response(BaseModel, Generic[T]):
    error: bool
    detail: str
    data: Optional[T] = None