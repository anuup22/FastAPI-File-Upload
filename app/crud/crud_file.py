from sqlalchemy.orm import Session
from app.models.database import FileMetadata

def create_file_metadata(db: Session, filename: str, file_location: str):
    file_metadata = FileMetadata(filename=filename, file_path=file_location)
    db.add(file_metadata)
    db.commit()
    db.refresh(file_metadata)
    return file_metadata

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