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

class ErrorResponse(BaseModel):
    detail: str

class Response(BaseModel, Generic[T]):
    data: Optional[T] = None
    error: Optional[ErrorResponse] = None