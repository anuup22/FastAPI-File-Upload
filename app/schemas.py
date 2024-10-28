from pydantic import BaseModel

class FileMetadataBase(BaseModel):
    filename: str
    file_path: str

class FileMetadataCreate(FileMetadataBase):
    pass

class FileMetadata(FileMetadataBase):
    id: int

    class Config:
        orm_mode: True