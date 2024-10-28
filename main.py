from fastapi import FastAPI, File, UploadFile, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from database import SessionLocal, FileMetadata, engine

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def save_file(file: UploadFile, file_location: str):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, _write_file, file, file_location)

def _write_file(file: UploadFile, file_location: str):
    with open(file_location, "wb") as f:
        while content := file.file.read(1024 * 1024):  # Read file in 1MB chunks
            f.write(content)

def save_file_metadata(db: Session, filename: str, file_location: str):
    file_metadata = FileMetadata(filename=filename, file_path=file_location)
    db.add(file_metadata)
    db.commit()
    db.refresh(file_metadata)

@app.get("/")
async def read_root():
    return {"msg": "Hello World"}

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
    if file_metadata is None:
        raise HTTPException(status_code=404, detail="File not found")
    return file_metadata