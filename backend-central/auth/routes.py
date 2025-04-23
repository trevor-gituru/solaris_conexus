# auth/routes.py
from auth.models import RegisterRequest
from db import models
from db.database import get_db
from fastapi import APIRouter, Depends, HTTPException
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

