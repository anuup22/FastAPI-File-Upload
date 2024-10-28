from sqlalchemy.orm import Session
from app.models.database import FileMetadata
from app.schemas import FileMetadataCreate

def create_file_metadata(db: Session, file_metadata: FileMetadataCreate):
    db_file_metadata = FileMetadata(**file_metadata.model_dump())
    db.add(db_file_metadata)
    db.commit()
    db.refresh(db_file_metadata)
    return db_file_metadata

def get_file_metadata(db: Session, file_id: int):
    return db.query(FileMetadata).filter(FileMetadata.id == file_id).first()

def get_files_metadata(db: Session):
    return db.query(FileMetadata).all()

def delete_file_metadata(db: Session, file_id: int):
    file_metadata = db.query(FileMetadata).filter(FileMetadata.id == file_id).first()
    if file_metadata:
        db.delete(file_metadata)
        db.commit()
    return file_metadata