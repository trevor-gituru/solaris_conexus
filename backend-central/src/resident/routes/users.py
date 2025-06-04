# /src/residents/routes/users.py
from fastapi import APIRouter, Depends
import random
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db.models import User, Profile
from src.resident.schemas.requests import ProfileRequest, ProfileUpdateRequest
from src.schemas.responses import DictResponse, MessageResponse
from src.utils.auth import auth_service  # ✅ Singleton AuthService
from src.utils.email import email_client  # ✅ Singleton AuthService
from src.utils.exception_handlers import DBExceptionHandler
from src.utils.logging import logger 
from src.utils.starknet import stark, sct

db_exception_handler = DBExceptionHandler()


router = APIRouter()

@router.get("/get", response_model=DictResponse)
async def get_profile(username: str = Depends(auth_service.get_username), db: Session = Depends(get_db)) -> DictResponse:
    logger.info(f"Profile fetch requested by username: {username}")
    # Fetch user with joined profile
    user = User.find_with_profile(db, username)
    db_exception_handler.check_user_authenticated(user)
    # Convert profile to dict
    profile = user.profile.to_dict() if user.profile else {}
    
    logger.info(f"Profile data returned for username: {username}")
    return DictResponse(data=profile)



@router.post("/create", response_model=MessageResponse)
def create_profile(
    profile_req: ProfileRequest,
    db: Session = Depends(get_db),
    username: str = Depends(auth_service.get_username)
):
    logger.info(f"Create profile request received for username: {username}")

     # 1) Find the current user
    user = User.find_with_profile(db, username=username)
    db_exception_handler.check_user_authenticated(user)

    # ✅ 2) Check if user already has a profile
    db_exception_handler.check_conflict(user.profile, message="Profile already exists")

    # 3) Build the data dictionary and link to that user
    data = profile_req.dict()
    data["user_id"] = user.id

    # 4) Create the Profile with exception handling
    new_profile = db_exception_handler.handle(lambda: Profile.create(db, data))

    message = f"Profile successfully created for user: {username}"
    logger.info(message)
    return MessageResponse(message=message)


@router.put("/update", response_model=MessageResponse)
def update_profile(update_req: ProfileUpdateRequest, db: Session = Depends(get_db), username: str = Depends(auth_service.get_username)):
    logger.info(f"Update profile request received for username: {username}")
    user = User.find(db, username=username)
    db_exception_handler.check_user_authenticated(user)

    updated_profile = db_exception_handler.handle(
        lambda: Profile.update(db, user_id=user.id, update_data=update_req.dict(exclude_unset=True))
    )

    logger.info(f"Profile updated successfully for user: {username}")
    return MessageResponse(message="Profile updated successfully")




@router.get("/confirm_email", response_model=DictResponse)
async def confirm_email(username: str = Depends(auth_service.get_username), db: Session = Depends(get_db)):
    logger.info(f"Confirm email request received for username: {username}")
    user = User.find(db, username=username)
    db_exception_handler.check_user_authenticated(user)
    
    confirmation_code = str(random.randint(100000, 999999))

    response = email_client.send_confirmation_email(
        to_name=user.username,
        to_email=user.email,
        confirmation_code=confirmation_code
    )

    logger.info(f"Confirm email sent successfully for username: {username}")
    return DictResponse(data={
        "code": confirmation_code
    })

@router.get("/details", response_model=DictResponse)
async def get_details(username: str = Depends(auth_service.get_username), db: Session = Depends(get_db)) -> DictResponse:
    logger.info(f"User Details request received for username: {username}")

    user = User.find(db, username=username)
    db_exception_handler.check_user_authenticated(user)

    device_count = 0
    strk_balance = 0.0
    sct_balance = 0.0

    profile = user.profile
    if profile:
        device_count = len(user.devices)
        account_address = profile.account_address

        try:
            strk_balance = await stark.balanceOf(account_address)
            sct_balance = await sct.balanceOf(account_address)
        except Exception as e:
            logger.warning(f"Balance fetch failed for {username}: {e}")
        else:
            logger.info(f"User details fetched successfully for {username}")


    return DictResponse(data={
        "nos_devices": device_count,
        "strk_balance": strk_balance,
        "sct_balance": sct_balance,
    })
    
