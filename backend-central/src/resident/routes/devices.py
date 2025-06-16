# /src/residents/routes/devices.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db.models import User, Device
from src.resident.schemas.requests import DeviceRequest, DeviceUpdateRequest
from src.schemas.responses import DictResponse, MessageResponse
from src.utils.auth import auth_service
from src.utils.exception_handlers import DBExceptionHandler
from src.utils.logging import logger

router = APIRouter()
db_exception_handler = DBExceptionHandler()

@router.get("/get", response_model=DictResponse)
async def get_device(username: str = Depends(auth_service.get_username), db: Session = Depends(get_db)) -> DictResponse:
    logger.info(f"Device fetch requested by username: {username}")

    # ✅ Fetch user by username
    user = User.find(db, username=username)
    db_exception_handler.check_user_authenticated(user)

    # ✅ Fetch single device from user (assuming one-to-one relationship)
    if user.devices:
        first_device = user.devices[0]
        device = first_device.to_dict()
    else:
        device = {}

    logger.info(f"Device data returned for username: {username}")
    return DictResponse(data=device)


@router.post("/create", response_model=MessageResponse)
def create_device(
    device_req: DeviceRequest,
    db: Session = Depends(get_db),
    username: str = Depends(auth_service.get_username)
):
    logger.info(f"Create device request received for username: {username}")
    user = User.find(db, username=username)
    db_exception_handler.check_user_authenticated(user)

    db_exception_handler.check_conflict(user.devices, message="Device already exists")

    data = device_req.dict()
    data["user_id"] = user.id

    new_device = db_exception_handler.handle(lambda: Device.create(db, data))

    message = f"Device successfully created for user: {username}"
    logger.info(message)
    return MessageResponse(message=message)

@router.put("/update", response_model=MessageResponse)
def update_device(
    update_req: DeviceUpdateRequest,
    db: Session = Depends(get_db),
    username: str = Depends(auth_service.get_username)
):
    logger.info(f"Update device request received for username: {username}")
    user = User.find(db, username=username)
    db_exception_handler.check_user_authenticated(user)

    updated_device = db_exception_handler.handle(
        lambda: Device.update(db, user_id=user.id, update_data=update_req.dict(exclude_unset=True))
    )

    logger.info(f"Device updated successfully for user: {username}")
    return MessageResponse(message="Device updated successfully")



from fastapi import WebSocket, WebSocketDisconnect 
from src.utils.mqtt import publish_command, register_listener
import asyncio


@router.websocket("/stream")
async def stream_power_readings(websocket: WebSocket, db: Session = Depends(get_db)):
    device_id = None
    try:
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=1008)
            return

        payload = auth_service.decode_token(token)
        if not payload or "sub" not in payload:
            await websocket.close(code=1008)
            return

        username = payload["sub"]
        user = User.find(db, username=username)
        if not user or not user.devices:
            await websocket.close(code=1008)
            return

        await websocket.accept()

        device = user.devices[0]
        device_id = device.id
        topic = f"{device.estate}/power/{device_id}"

        queue = asyncio.Queue()
        loop = asyncio.get_running_loop()

        async def async_mqtt_callback(data):
            await queue.put(data)

        def mqtt_callback(data):
            print("[MQTT] Callback received:", data)
            asyncio.run_coroutine_threadsafe(async_mqtt_callback(data), loop)

        register_listener(topic, mqtt_callback, loop=loop)

        publish_command(f"{device.estate}/commands", {
            "device": device_id,
            "command": "stream"
        })


        while True:
            TIMEOUT_SECONDS = 10
            data = await asyncio.wait_for(queue.get(), timeout=TIMEOUT_SECONDS)
            await websocket.send_json(data)
    except asyncio.TimeoutError:
        print(f"[WebSocket] Timeout waiting for data from device {device_id}")
        await websocket.close(code=1011, reason="No data received in time")
    except WebSocketDisconnect:
        print(f"[WebSocket] Disconnected: {device_id}")
    except Exception as e:
        print(f"[WebSocket Error] {e}")
        try:
            await websocket.close()
        except:
            pass
    finally:
        if device_id:
            print(f"[WebSocket] Stopping stream for device {device_id}")
            publish_command(f"{device.estate}/commands", {
                "device": device_id,
                "command": "stop"
            })

@router.get("/toggle")
async def toggle_device(
    username: str = Depends(auth_service.get_username),
    db: Session = Depends(get_db)
):
    # Fetch the user first
    logger.info(f"Toggle device request received for username: {username}")
    user = User.find(db, username=username)
    db_exception_handler.check_user_authenticated(user)


    # Fetch device with id 5 belonging to this user
    device = user.devices[0]
    if not device:
        raise HTTPException(status_code=404, detail=f"User {user.username} has no device registered")

    device_id = device.id

    publish_command(f"{device.estate}/commands", {
        "device": device_id,
        "instruction": 2
    })

    return {"message": f"Successfully toggled {device.device_id}"}
