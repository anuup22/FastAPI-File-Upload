from fastapi import FastAPI
from app.routers import file

app = FastAPI()

app.include_router(file.router)