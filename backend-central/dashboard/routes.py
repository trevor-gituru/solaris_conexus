# dashboard/routes.py
from dashboard.models import ProfileRequest, DeviceRequest
from db import models
from db.database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from auth.utils import get_current_username
from sqlalchemy.orm import Session, joinedload
from dashboard.utils import send_email, fetch_and_create_wallets
import random

router = APIRouter()

@router.post(
    "/create_profile",
    status_code=status.HTTP_201_CREATED,
    summary="Create a profile for the authenticated user",
)
def create_profile_route(
    profile_req: ProfileRequest,                                  # ← your imported model
    db: Session = Depends(get_db),
    username: str = Depends(get_current_username),                # ← enforces & injects JWT 'sub'
):
    # 1) find the current user
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authenticated user not found",
        )

    # 2) build the data dictionary and link to that user
    data = profile_req.dict()
    data["user_id"] = user.id

    # 3) create the Profile
    new_profile = models.create_profile(db, data)

    return new_profile


@router.get("/confirm_email")
async def email(username: str = Depends(get_current_username), db: Session = Depends(get_db)):
    # Fetch user from the database using username
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    to_name = user.username
    to_email = user.email
    confirmation_code = str(random.randint(100000, 999999))

    body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: auto; padding: 20px;">
          <h2 style="color: #4CAF50;">Email Confirmation</h2>
          <p>Hi {to_name},</p>

          <p>Thank you for signing up with Solaris Connexus!</p>

          <p>Please confirm your email address by copying and entering the following code:</p>

          <div style="text-align: center; margin: 30px 0;">
            <span style="font-size: 24px; font-weight: bold; color: #4CAF50;">{confirmation_code}</span>
          </div>

          <p>If you did not request this email, you can safely ignore it.</p>

          <p>Best regards,<br>
          The Solaris Connexus Team</p>

          <hr style="margin-top: 40px;">
          <p style="font-size: 12px; color: #999;">This is an automated message. Please do not reply directly to this email.</p>
        </div>
      </body>
    </html>
    """

    # Call your helper to send email
    response = send_email(
        subject="RE: Confirmation Email",
        body=body,
        to_name=to_name,
        to_email=to_email
    )

    return {"detail": "Confirmation email sent successfully", "code": confirmation_code}


@router.get("/get_profile")
async def get_profile(username: str = Depends(get_current_username), db: Session = Depends(get_db)):
    # Fetch user with profile
    user = db.query(models.User).filter(models.User.username == username).options(joinedload(models.User.profile)).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Assign a wallet if not already assigned
    wallet = models.assign_wallet_to_user(db, user.id)

    # Convert profile to dict
    profile = user.profile.to_dict() if user.profile else {}

    # Add wallet address to the profile
    if wallet:
        profile["wallet_address"] = wallet.account_address
    else:
        profile["wallet_address"] = None  # Or handle differently

    return profile


@router.post("/create_device")
async def create_device(device: DeviceRequest, username: str = Depends(get_current_username), db: Session = Depends(get_db)):
    # Get the user who is creating the device
    user = db.query(models.User).filter(models.User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if device_id is already taken
    existing_device = db.query(models.Device).filter(models.Device.device_id == device.device_id).first()
    if existing_device:
        raise HTTPException(status_code=400, detail="Device ID already exists")

    # Create new device
    new_device = models.Device(
        device_type=device.device_type,
        device_id=device.device_id,
        connection_type=device.connection_type,
        estate=device.estate,
        status="inactive",  # Default status
        pin_loads=device.pin_loads,
        user_id=user.id
    )

    db.add(new_device)
    db.commit()
    db.refresh(new_device)

    return {"message": "Device created successfully", "device": new_device.to_dict()}

@router.get("/get_devices")
async def get_devices(username: str = Depends(get_current_username), db: Session = Depends(get_db)):
    # Fetch the user first
    user = db.query(models.User).filter(models.User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Fetch all devices belonging to this user
    devices = db.query(models.Device).filter(models.Device.user_id == user.id).all()

    # Format the devices nicely
    device_list = [device.to_dict() for device in devices]

    return {"devices": device_list}





from fastapi.responses import StreamingResponse
import serial
import time



# # Set up the serial port (adjust port/baudrate as needed)
# ser = serial.Serial(
#     port='/dev/ttyACM0',
#     baudrate=9600,
#     timeout=1
# )
# time.sleep(2)  # give the device time to reset/stabilize

# def power_event_stream():
#     """
#     Continuously read lines of the form "2.53, 0.16" from serial,
#     compute power = voltage * current, and yield as SSE.
#     """
#     while True:
#         if ser.in_waiting > 0:
#             line = ser.readline().decode('utf-8').strip()
#             try:
#                 # parse voltage and current
#                 v_str, i_str = line.split(',')
#                 voltage = float(v_str.strip())
#                 current = float(i_str.strip())
#                 power = voltage * current
#                 # yield as a Server-Sent Event
#                 yield f"data: {power:.4f}\n\n"
#             except Exception:
#                 # if parsing fails, just skip this line
#                 continue
#         time.sleep(0.1)  # avoid busy‐looping

# @router.get("/stream_power")
# def stream_power():
#     """
#     SSE endpoint that streams the instantaneous power (in Watts)
#     as "data: <power>\n\n" whenever a new serial reading arrives.
#     """
#     return StreamingResponse(
#         power_event_stream(),
#         media_type="text/event-stream"
#     )

@router.get("/setup_accounts")
def setup_accounts(db: Session = Depends(get_db)):
    """
    SSE endpoint that streams the instantaneous power (in Watts)
    as "data: <power>\n\n" whenever a new serial reading arrives.
    """
    fetch_and_create_wallets(db)
    return {"detail": "Wallets created successfully"}