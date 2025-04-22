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



# Define a Pydantic model for request validation
class User(BaseModel):
    username: str
    email: str
    password: str

@app.post("/register")
async def register_user(user: User):
    # Logic to handle registration
    return {"message": "User registered successfully!", "user": user}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

