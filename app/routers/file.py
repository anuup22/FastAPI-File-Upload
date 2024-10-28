from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
import asyncio
from concurrent.futures import ThreadPoolExecutor
from app.models.database import SessionLocal
from app.crud import crud_file

router = APIRouter()

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

@router.post("/uploadfile/")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_location = f"uploads/{file.filename}"
    background_tasks.add_task(save_file, file, file_location)
    background_tasks.add_task(crud_file.create_file_metadata, db, file.filename, file_location)
    return {"info": f"file '{file.filename}' will be saved at '{file_location}'"}

@router.get("/files/")
async def get_files(db: Session = Depends(get_db)):
    return {"files": crud_file.get_files_metadata(db)}

@router.get("/file/{file_id}")
async def get_file(file_id: int, db: Session = Depends(get_db)):
    file_metadata = crud_file.get_file_metadata(db, file_id)
    if file_metadata is None:
        raise HTTPException(status_code=404, detail="File not found")
    return file_metadata