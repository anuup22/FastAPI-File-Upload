from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from app.models.database import SessionLocal
from app.crud import crud_file
from app.schemas import FileMetadata, FileMetadataCreate, Response

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def save_file(file_content: bytes, file_location: str):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, _write_file, file_content, file_location)

def _write_file(file_content: bytes, file_location: str):
    with open(file_location, "wb") as f:
        f.write(file_content)

@router.post("/uploadfile/", response_model=Response[FileMetadata])
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_location = f"uploads/{file.filename}"
    file_content = await file.read()  # Read the file content in the main thread
    background_tasks.add_task(save_file, file_content, file_location)
    file_metadata_create = FileMetadataCreate(filename=file.filename, file_path=file_location)
    db_file_metadata = crud_file.create_file_metadata(db, file_metadata_create)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=Response(detail="File uploaded successfully", data=db_file_metadata).model_dump())

@router.get("/files/", response_model=Response[list[FileMetadata]])
async def get_files(db: Session = Depends(get_db)):
    files_metadata = crud_file.get_files_metadata(db)
    return JSONResponse(status_code=status.HTTP_200_OK, content=Response(detail="Fetched successfully", data=files_metadata).model_dump())

@router.get("/file/{file_id}", response_model=Response[FileMetadata])
async def get_file(file_id: int, db: Session = Depends(get_db)):
    file_metadata = crud_file.get_file_metadata(db, file_id)
    if file_metadata is None:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=Response(error=True, detail="File not found").model_dump())
    return JSONResponse(status_code=status.HTTP_200_OK, content=Response(detail="Fetched successfully", data=file_metadata).model_dump())

@router.delete("/file/{file_id}", response_model=Response[FileMetadata])
async def delete_file(file_id: int, db: Session = Depends(get_db)):
    file_metadata = crud_file.get_file_metadata(db, file_id)
    if file_metadata is None:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=Response(error=True, detail="File not found").model_dump())

    # Remove the file from the server
    if os.path.exists(file_metadata.file_path):
        os.remove(file_metadata.file_path)

    # Remove the file metadata from the database
    crud_file.delete_file_metadata(db, file_id)

    return JSONResponse(status_code=status.HTTP_200_OK, content=Response(detail="Deleted successfully").model_dump())