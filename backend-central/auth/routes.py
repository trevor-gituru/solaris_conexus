# auth/routes.py
from auth.models import RegisterRequest, LoginRequest
from auth.utils import verify_password, create_access_token, decode_token
from db import models
from db.database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session



router = APIRouter()

@router.post("/register")
async def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(
        (models.User.username == request.username) | 
        (models.User.email == request.email)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    models.create_user(db, request)
    return {"message": "Successfully registered. Please login."}

@router.post("/login")
async def login_user(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    # Create access token
    access_token = create_access_token(data={"sub": user.username})

    return {"access_token": access_token, "token_type": "bearer"}    


