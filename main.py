from fastapi import FastAPI, File, UploadFile, Depends
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

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_location = f"uploads/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())

    file_metadata = FileMetadata(filename=file.filename, file_path=file_location)
    db.add(file_metadata)
    db.commit()
    db.refresh(file_metadata)

    return {"info": f"file '{file.filename}' saved at '{file_location}'", "file_id": file_metadata.id}

@app.get("/files/")
async def get_files(db: Session = Depends(get_db)):
    return {"files": db.query(FileMetadata).all()}

@app.get("/file/{file_id}")
async def get_file(file_id: int, db: Session = Depends(get_db)):
    file_metadata = db.query(FileMetadata).filter(FileMetadata.id == file_id).first()
    if not file_metadata:
        return {"error": "File not found"}
    return {"file_metadata": file_metadata}