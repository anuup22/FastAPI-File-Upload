from fastapi import FastAPI, File, UploadFile
import os

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    file_location = f"uploads/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())
    return {"info": f"file '{file.filename}' saved at '{file_location}'"}