# /src/resident/routes/__init__.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from .users import router as user_router
from .devices import router as device_router
from .token_purchase import router as token_router
from .trade import router as trade_router


router = APIRouter()

router.include_router(user_router, prefix="/user_profile", tags=["User Details"])
router.include_router(device_router, prefix="/device", tags=["Devices"])
router.include_router(token_router, prefix="/token_purchase", tags=["SCT Token Purchase"])
router.include_router(trade_router, prefix="/trade", tags=["Trade SCT"])

