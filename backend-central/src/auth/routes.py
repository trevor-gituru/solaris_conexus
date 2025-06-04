# /src/auth/routes.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from src.auth.requests import RegisterRequest, LoginRequest
from src.auth.responses import TokenResponse
from src.db.models import User  # ✅ Direct import of User model
from src.db.database import get_db
from src.utils.auth import auth_service  # ✅ Singleton AuthService
from src.utils.logging import logger
from src.schemas.responses import MessageResponse
from src.utils.exception_handlers import DBExceptionHandler

db_exception_handler = DBExceptionHandler(
    integrity_message="Username or email already exists",
    general_message="Something went wrong while saving",
    conflict_message="Username or email already exists"
)

router = APIRouter()

@router.post("/register", response_model=MessageResponse)
async def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    logger.info(f"Register request received for username: {request.username}")
    existing = User.find(db, username=request.username, email=request.email)
    
    db_exception_handler.check_conflict(existing)
    db_exception_handler.handle(lambda: User.create(db, request))
    message = f"User registered successfully: {request.username}"
    logger.info(message)
    return MessageResponse(message=message)

@router.post("/login", response_model=TokenResponse)
async def login_user(request: LoginRequest, db: Session = Depends(get_db)):
    logger.info(f"Login request received for email: {request.email}")
    user = User.find(db, email = request.email)
    db_exception_handler.check_auth(
        user is not None and auth_service.verify_password(request.password, user.hashed_password)
    )
    access_token = auth_service.create_access_token(data={"sub": user.username})
    logger.info(f"User logged in successfully: {user.username}")

    return TokenResponse(access_token=access_token, token_type="bearer")


