# src/hubs/routes.py
from src.db.models.hubs import Hub
from src.db.database import get_db
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from src.hubs.requests import HubCreateRequest, DeviceRequest, TokenConsumptionRequest
from src.utils.exception_handlers import DBExceptionHandler   
from src.schemas.responses import ListDictResponse, DictResponse, MessageResponse
from src.utils.logging import logger 
from src.utils.auth import auth_service  # ✅ Singleton AuthService
from src.auth.responses import TokenResponse
from src.utils.notifications import notification_manager 

router = APIRouter()
db_exception_handler = DBExceptionHandler()

@router.post("/create", response_model=DictResponse)
def create_hub(hub_data: HubCreateRequest, db: Session = Depends(get_db)):
    logger.info(f"Hub creation requested")
    # Optional: check if hub name already exists
    hub = Hub.find(db, name=hub_data.name) 
    db_exception_handler.check_auth(
        condition=hub is not None,
        message="Hub already exist"
    )


    new_hub = Hub.create(db, name=hub_data.name)
    logger.info(f"Hub creation successful")
    return DictResponse(data=new_hub.to_dict())
 

@router.post("/connect", response_model=TokenResponse)
def connect_hub(api_key: str = Query(..., description="API key of the hub"), db: Session = Depends(get_db)):
    hub = Hub.connect(db, api_key)
    db_exception_handler.check_auth(
        condition=hub is not None,
        message="Hub not found"
    )
    access_token = auth_service.create_access_token(data={"sub": hub.name}, expires_minutes=60)
    logger.info(f"{hub.name} Hub successfully connected")

    return TokenResponse(access_token=access_token, token_type="bearer")

@router.get("/sync_devices", response_model=ListDictResponse)
def hub_devices(name: str = Depends(auth_service.get_username), db: Session = Depends(get_db)):
    hub = Hub.find(db, name=name)
    db_exception_handler.check_auth(
        condition=hub is not None,
        message="Hub not found"
    )
    devices_list = [device.to_hub_dict() for device in hub.devices]
    logger.info(f"{hub.name} Hub synchronization of {len(devices_list)} devices requested")
    return ListDictResponse(data=devices_list)

@router.post("/shutdown", response_model=MessageResponse)
def shutdown_hub(name: str = Depends(auth_service.get_username), db: Session = Depends(get_db)):
    hub = Hub.close(db, name=name)
    db_exception_handler.check_auth(
        condition=hub is not None,
        message="Hub not found"
    )
    device_list = hub.devices
    for device in device_list:
        db_exception_handler.handle(lambda d=device: d.close(db))
    message = f"{hub.name} Hub shutdown successful. {len(device_list)} devices made inactive"
    logger.info(message)
    return MessageResponse(message=message)

@router.post("/activate_device", response_model=MessageResponse)
def activate_device(req: DeviceRequest, name: str = Depends(auth_service.get_username), db: Session = Depends(get_db)):
    hub = Hub.find(db, name=name)
    db_exception_handler.check_auth(
        condition=hub is not None,
        message="Hub not found"
    )
    device_list = hub.devices
    device_id = req.dict().get("device_id")
    db_exception_handler.check_auth(
        condition=device_id is not None,
        message="Device not specified"
    )
    logger.info(f"{hub.name} Hub requested activation of {device_id}")
    device = next((d for d in device_list if d.device_id == device_id), None)
    db_exception_handler.check_auth(
        condition=device is not None,
        message="Device not found"
    )
    db_exception_handler.handle(lambda d=device: d.activate(db))
    message = f"{hub.name} Hub successfully made {device_id} {device.status}"
    logger.info(message)
    return MessageResponse(message=message)



@router.post("/deactivate_device", response_model=MessageResponse)
def deactivate_device(req: DeviceRequest, name: str = Depends(auth_service.get_username), db: Session = Depends(get_db)):
    hub = Hub.find(db, name=name)
    db_exception_handler.check_auth(
        condition=hub is not None,
        message="Hub not found"
    )
    device_list = hub.devices
    device_id = req.dict().get("device_id")
    db_exception_handler.check_auth(
        condition=device_id is not None,
        message="Device not specified"
    )
    logger.info(f"{hub.name} Hub requested deactivation of {device_id}")
    device = next((d for d in device_list if d.device_id == device_id), None)
    db_exception_handler.check_auth(
        condition=device is not None,
        message="Device not found"
    )
    db_exception_handler.handle(lambda d=device: d.close(db))
    message = f"{hub.name} Hub successfully made {device_id} {device.status}"
    logger.info(message)
    return MessageResponse(message=message)


@router.post("/token_consumption", response_model=MessageResponse)
def token_consumption(req: TokenConsumptionRequest, name: str = Depends(auth_service.get_username), db: Session = Depends(get_db)):
    hub = Hub.find(db, name=name)
    db_exception_handler.check_auth(
        condition=hub is not None,
        message="Hub not found"
    )
    device_list = hub.devices
    device_id = req.dict().get("device_id")
    db_exception_handler.check_auth(
        condition=device_id is not None,
        message="Device not specified"
    )
    logger.info(f"{hub.name} Hub requested notification of {device_id} for consume 1 SCT")
    device = next((d for d in device_list if d.device_id == device_id), None)
    db_exception_handler.check_auth(
        condition=device is not None,
        message="Device not found"
    )
    user = device.user
    notification_manager.notify_token_consumption(req.dict(), user)
    message = f"Successfully notified [{user.username}] - [{device_id}] of token consumption"
    logger.info(message)
    return MessageResponse(message=message)

