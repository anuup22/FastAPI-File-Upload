from fastapi import FastAPI
from app.routers import file

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application!"}

app.include_router(file.router)