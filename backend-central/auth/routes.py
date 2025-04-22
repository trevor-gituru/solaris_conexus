# auth/routes.py
from fastapi import APIRouter
from .models import RegisterRequest
from .utils import hash_password

router = APIRouter()

@router.post("/register")
async def register_user(user: RegisterRequest):
    # Logic to save user to database or validate uniqueness etc.
    return {"message": "User registered successfully", "user": user}