# hubs/routes.py
from src.db.models.hubs import Hub
from src.db.database import get_db
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from src.hubs.models import HubCreateRequest
from typing import List

router = APIRouter()

@router.post("/create")
def create_hub(hub_data: HubCreateRequest, db: Session = Depends(get_db)):
    # Optional: check if hub name already exists
    existing = db.query(Hub).filter(Hub.name == hub_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Hub with this name already exists")

    new_hub = Hub.create(db, name=hub_data.name)

    return {
        "id": new_hub.id,
        "name": new_hub.name,
        "api_key": new_hub.api_key,
        "registered_at": new_hub.registered_at.isoformat(),
        "last_active": new_hub.last_active.isoformat() if new_hub.last_active else None,
    }


@router.get("/devices")
def get_devices_by_api_key(api_key: str = Query(..., description="API key of the hub"), db: Session = Depends(get_db)):
    hub = db.query(Hub).filter(Hub.api_key == api_key).first()
    if not hub:
        raise HTTPException(status_code=404, detail="Hub not found")

    devices_list = []
    for device in hub.devices:
        # Get account address from profile through user
        account_address = (
            device.user.profile.account_address
            if device.user and device.user.profile
            else None
        )

        devices_list.append({
            "id": device.id,
            "device_type": device.device_type,
            "device_id": device.device_id,
            "connection_type": device.connection_type,
            "estate": device.estate,
            "status": device.status,
            "pin_loads": device.pin_loads,
            "created_at": device.created_at.isoformat() if device.created_at else None,
            "user_id": device.user_id,
            "account_address": account_address  # Include it here
        })

    return {"devices": devices_list}

