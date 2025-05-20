# dashboard/routes.py
from dashboard.models import ProfileRequest, DeviceRequest, TokenPurchaseRequest, TradeRequest, CancelTradeRequest, AcceptTradeRequest
from db import models
from db.database import get_db
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from auth.utils import get_current_username, decode_token
from sqlalchemy.orm import Session, joinedload
from dashboard.utils import send_email, fetch_and_create_wallets
from dashboard.starknet import stark, sct
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
    print(data)
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

    # Convert profile to dict
    profile = user.profile.to_dict() if user.profile else {}

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



@router.post(
    "/add_token_purchase",
    status_code=status.HTTP_201_CREATED,
    summary="Buy tokens and record purchase for the authenticated user",
)
async def add_token_purchase(
    purchase_req: TokenPurchaseRequest,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_username),
):
    # 1) Find the current user and their profile
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not user.profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authenticated user or profile not found",
        )

    # 2) Get the buyer address from the user's profile
    buyer_address = user.profile.account_address
    if not buyer_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no StarkNet account address associated with their profile",
        )

    # 3) Call StarkNet contract to buy tokens
    try:
        tx_hash = await sct.buy_tokens(buyer_address=buyer_address, amount=purchase_req.amount_stc)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Blockchain transaction failed: {str(e)}",
        )

    # 4) Prepare purchase data
    data = purchase_req.dict()
    data["tx_hash"] = tx_hash
    data["user_id"] = user.id

    # 5) Save to DB
    new_purchase = models.create_token_purchase(db, data, user.id)

    return new_purchase



@router.get(
    "/get_token_purchases",
    status_code=status.HTTP_200_OK,
    summary="Get all token purchases for the authenticated user",
)
def get_token_purchases(
    db: Session = Depends(get_db),
    username: str = Depends(get_current_username),
):
    # 1) Get the user
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authenticated user not found",
        )

    # 2) Query all TokenPurchase records for the user
    purchases = db.query(models.TokenPurchase).filter(models.TokenPurchase.user_id == user.id).order_by(models.TokenPurchase.date.desc()).all()

    # 3) Return as list of dicts
    return [
        {
            "date": purchase.date.isoformat(),
            "tx_hash": purchase.tx_hash,
            "amount_stc": float(purchase.amount_stc),
            "strk_used": float(purchase.strk_used),
        }
        for purchase in purchases
    ]


@router.post(
    "/create_trade",
    status_code=status.HTTP_201_CREATED,
    summary="Create a trade request for the authenticated user",
)
async def create_trade(
    trade_req: TradeRequest,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_username),
):
    # 1) Find the current user and their profile
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not user.profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authenticated user or profile not found",
        )

   
    # 3) Prepare trade data
    data = trade_req.dict()
    data["user_id"] = user.id

    # 4) Save to DB
    new_trade = models.create_trade_request(db, data, user.id)
                       
    return new_trade

@router.get("/get_user_trade")
async def get_user_trade(username: str = Depends(get_current_username), db: Session = Depends(get_db)):
    # 1) Get the current user
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2) Get all trades where the user is the creator or buyer
    trades = db.query(models.TradeRequest).filter(
        (models.TradeRequest.user_id == user.id) |
        (models.TradeRequest.buyer_id == user.id)
    ).all()

    # 3) Format the results
    trade_list = []
    for trade in trades:
        is_buyer = trade.buyer_id == user.id
        trade_creator = db.query(models.User).filter(models.User.id == trade.user_id).first()

        trade_dict = {
            "id": trade.id,
            "date": trade.date,
            "tx_hash": trade.tx_hash,
            "stc_offered": str(trade.stc_offered),
            "strk_price": str(trade.strk_price),
            "status": "Bought" if is_buyer else trade.status,
            "buyer": trade_creator.username if is_buyer else None,
        }

        # If user is not the buyer and buyer exists, show actual buyer username
        if not is_buyer and trade.buyer_id:
            buyer = db.query(models.User).filter(models.User.id == trade.buyer_id).first()
            trade_dict["buyer"] = buyer.username if buyer else None

        trade_list.append(trade_dict)

    return {"trades": trade_list}

@router.post("/cancel_trade")
async def cancel_trade(
    request: CancelTradeRequest,
    username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
):
    # 1) Verify user
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2) Find trade by ID
    trade = db.query(models.TradeRequest).filter(models.TradeRequest.id == request.trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")

    # 3) Check ownership
    if trade.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this trade")

    # 4) Update status and tx_hash
    trade.status = "Cancelled"
    trade.tx_hash = request.tx_hash
    trade.date = datetime.utcnow()

    db.commit()
    db.refresh(trade)

    # 5) Return updated trade dict
    trade_dict = {
        "id": trade.id,
        "date": trade.date,
        "tx_hash": trade.tx_hash,
        "stc_offered": str(trade.stc_offered),
        "strk_price": str(trade.strk_price),
        "status": trade.status,
        "buyer": None,
    }

    if trade.buyer_id:
        buyer = db.query(models.User).filter(models.User.id == trade.buyer_id).first()
        trade_dict["buyer"] = buyer.username if buyer else None

    return {"message": "Trade cancelled successfully", "trade": trade_dict}


@router.get("/get_user_details")
async def get_user_details(username: str = Depends(get_current_username), db: Session = Depends(get_db)):
    # Fetch user with joined profile
    user = db.query(models.User).filter(models.User.username == username).options(joinedload(models.User.profile)).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # If profile doesn't exist, return zeros
    if not user.profile or not user.profile.account_address:
        return {
            "nos_devices": 0,
            "strk_balance": 0.0,
            "sct_balance": 0.0
        }

    # Get device count
    device_count = db.query(models.Device).filter(models.Device.user_id == user.id).count()
    # Get balances
    account_address = user.profile.account_address
    try:
        strk_balance = await stark.balanceOf(account_address)
    except Exception as e:
        strk_balance = 0.0
        print("strk erro", e)

    try:
        sct_balance = await sct.balanceOf(account_address)
    except Exception as e:
        sct_balance = 0.0
        print("sct erro", e)
    return {
        "nos_devices": device_count,
        "strk_balance": strk_balance,
        "sct_balance": sct_balance
    }

@router.get("/get_free_trade")
async def get_free_trade(username: str = Depends(get_current_username), db: Session = Depends(get_db)):
    # 1) Get the current user
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2) Get pending trades not created by the current user
    trades = (
        db.query(models.TradeRequest)
        .filter(
            models.TradeRequest.status == "pending",
            models.TradeRequest.user_id != user.id
        )
        .all()
    )

    # 3) Format results
    trade_list = []
    for trade in trades:
        trade_dict = {
            "id": trade.id,
            "date": trade.date,
            "tx_hash": trade.tx_hash,
            "stc_offered": str(trade.stc_offered),
            "strk_price": str(trade.strk_price),
            "status": trade.status,
        }       
        trade_list.append(trade_dict)

    return {"trades": trade_list}

@router.post(
    "/accept_trade",
    status_code=status.HTTP_201_CREATED,
    summary="Accept trade requests for the authenticated user",
)
async def accept_trade(
    trade_req: AcceptTradeRequest,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_username),
):
    # 1) Find the current user and their profile
    print(trade_req)
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not user.profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authenticated user or profile not found",
        )

    # 2) Get the buyer address from the user's profile
    buyer_address = user.profile.account_address
    if not buyer_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no StarkNet account address associated with their profile",
        )

    # 3) Call StarkNet contract to buy tokens
    trade_id = trade_req.trade_contract_id
    amount = trade_req.sct_offered 
    try:
        tx_hash = await sct.signTrade(buyer_address=buyer_address, amount=amount, trade_id=trade_id )
        trade_id = trade_req.trade_backend_id
        trade = db.query(models.TradeRequest).filter(models.TradeRequest.id == trade_id).first()
        if trade:
            trade.status = "Complete"
            trade.tx_hash = tx_hash
            trade.date = datetime.utcnow()
            trade.buyer_id = user.id
            db.commit()
            db.refresh(trade)
            return ("success")
        else:
            raise ValueError("Trade not found")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Blockchain transaction failed: {str(e)}",
        )




# from fastapi.responses import StreamingResponse
# import serial
# import time



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

# @router.get("/setup_accounts")
# def setup_accounts(db: Session = Depends(get_db)):
#     """
#     SSE endpoint that streams the instantaneous power (in Watts)
#     as "data: <power>\n\n" whenever a new serial reading arrives.
#     """
#     fetch_and_create_wallets(db)
#     return {"detail": "Wallets created successfully"}

# @router.websocket("/ws/stream")
# async def stream_power_readings(websocket: WebSocket, username: str = Depends(get_current_username), db: Session = Depends(get_db)):
#     await websocket.accept()

#     # 1. Get user
#     user = db.query(models.User).filter(models.User.username == username).first()
#     if not user:
#         await websocket.send_json({"error": "User not found"})
#         await websocket.close()
#         return

#     # 2. Get first device
#     device = db.query(models.Device).filter(models.Device.user_id == user.id).first()
#     if not device:
#         await websocket.send_json({"error": "No devices found"})
#         await websocket.close()
#         return

#     device_id = device.id
#     topic = f"juja/power/{device_id}"

#     queue = asyncio.Queue()

#     def mqtt_callback(data):
#         asyncio.create_task(queue.put(data))  # Pass data to the asyncio event loop

#     # 3. Register MQTT listener
#     register_listener(topic, mqtt_callback)

#     # 4. Publish stream start command
#     publish_command("juja/commands", {
#         "device": device_id,
#         "command": "stream"
#     })

#     try:
#         while True:
#             data = await queue.get()
#             await websocket.send_json(data)

#     except WebSocketDisconnect:
#         print(f"[WebSocket] Disconnected: stopping stream for device {device_id}")
#         publish_command("juja/commands", {
#             "device": device_id,
#             "command": "stop"
#         })
#     except Exception as e:
#         print(f"[WebSocketError] {e}")
#         await websocket.close()

from fastapi import WebSocket, WebSocketDisconnect 
from mqtt.client import publish_command, register_listener
import asyncio


@router.websocket("/device/stream")
async def stream_power_readings(websocket: WebSocket, db: Session = Depends(get_db)):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)  # Policy violation
        return

    payload = decode_token(token)
    if not payload or "sub" not in payload:
        await websocket.close(code=1008)
        return

    username = payload["sub"]
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        await websocket.close(code=1008)
        return

    await websocket.accept()

    device = db.query(models.Device).filter(models.Device.user_id == user.id).first()
    if not device:
        await websocket.send_json({"error": "Device with ID 5 not found"})
        await websocket.close()
        return

    device_id = device.id
    topic = f"juja/power/{device_id}"

    queue = asyncio.Queue()
    loop = asyncio.get_running_loop()

    async def async_mqtt_callback(data):
        await queue.put(data)

    def mqtt_callback(data):
        asyncio.run_coroutine_threadsafe(async_mqtt_callback(data), loop)

    register_listener(topic, mqtt_callback, loop=loop)

    publish_command("juja/commands", {
        "device": device_id,
        "command": "stream"
    })

    try:
        while True:
            data = await queue.get()
            await websocket.send_json(data)
    except WebSocketDisconnect:
        print(f"[WebSocket] Disconnected: stopping stream for device {device_id}")
        
    except Exception as e:
        print(f"[WebSocketError] {e}")
        await websocket.close()
    finally:
        publish_command("juja/commands", {
        "device": device_id,
        "command": "stop"
    })

@router.get("/toggle_device")
async def toggle_device(
    username: str = Depends(get_current_username),
    db: Session = Depends(get_db)
):
    # Fetch the user first
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Fetch device with id 5 belonging to this user
    device = db.query(models.Device).filter(models.Device.user_id == user.id, models.Device.user_id == user.id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device with ID 5 not found for this user")

    device_id = device.id

    publish_command("juja/commands", {
        "device": device_id,
        "instruction": 2
    })

    return {"message": f"Successfully toggled {device.device_id}"}
