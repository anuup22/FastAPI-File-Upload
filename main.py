from fastapi import FastAPI, File, UploadFile, Depends, BackgroundTasks
from sqlalchemy.orm import Session
import os
from database import SessionLocal, FileMetadata, engine

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

async def save_file(file: UploadFile, file_location: str):
    with open(file_location, "wb") as f:
        while content := await file.read(1024 * 1024):  # Read file in 1MB chunks
            f.write(content)

def save_file_metadata(db: Session, filename: str, file_location: str):
    file_metadata = FileMetadata(filename=filename, file_path=file_location)
    db.add(file_metadata)
    db.commit()
    db.refresh(file_metadata)

@app.post("/uploadfile/")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_location = f"uploads/{file.filename}"
    background_tasks.add_task(save_file, file, file_location)
    background_tasks.add_task(save_file_metadata, db, file.filename, file_location)
    return {"info": f"file '{file.filename}' will be saved at '{file_location}'"}

@app.get("/files/")
async def get_files(db: Session = Depends(get_db)):
    return {"files": db.query(FileMetadata).all()}

@app.get("/file/{file_id}")
async def get_file(file_id: int, db: Session = Depends(get_db)):
    file_metadata = db.query(FileMetadata).filter(FileMetadata.id == file_id).first()
    if not file_metadata:
        return {"error": "File not found"}
    return {"file_metadata": file_metadata}