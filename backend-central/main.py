from auth.routes import router as auth_router
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Get the CORS origins from the environment variable
allowed_origins = os.getenv("CORS_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Adjust if using different host
    allow_credentials=True,
    allow_methods=["*"],  # Accept all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Accept all headers
)

from db.database import engine, Base
from db.models import User

# Create tables
Base.metadata.create_all(bind=engine)

app.include_router(auth_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

