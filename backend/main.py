from fastapi import FastAPI
from uvicorn import run

from dto_model import CustomException
from exception_handler import exception_handler
from router import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your frontend's origin
    allow_credentials=True,
    allow_methods=["*"],  # Adjust this to allow other methods like "OPTIONS", "POST", etc.
    allow_headers=["*"],
)

app.add_exception_handler(CustomException, exception_handler)

app.include_router(router)