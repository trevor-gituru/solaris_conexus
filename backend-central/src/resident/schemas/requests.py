
# src/residentschemas/requests.py
from pydantic import BaseModel, constr, condecimal, Field, validator
from datetime import date, datetime
from typing import Optional, List, Dict
from enum import Enum

# Optional: Use Enum for better validation (example for gender)
class GenderEnum(str, Enum):
    male = "Male"
    female = "Female"
    other = "Other"

class NotificationType(str, Enum):
    sms = "sms"
    email = "email"
    none = ""

class ProfileRequest(BaseModel):
    first_name: constr(min_length=2, max_length=50)  # First name should be between 2 and 50 characters
    last_name: constr(min_length=2, max_length=50)   # Last name should be between 2 and 50 characters
    dob: date  # Date of birth
    gender: GenderEnum  # Gender: "Male", "Female", "Other"
    phone: Optional[constr(max_length=15)] = None  # Phone number is optional, max length 15 characters
    account_address: Optional[constr(max_length=100)] = None  # Account address is optional, max length 100

    class Config:
        extra = "forbid"  # Disallow extra fields

class ProfileUpdateRequest(BaseModel):
    phone: Optional[constr(max_length=15)] = None
    phone2: Optional[constr(max_length=15)] = None
    notification: Optional[constr(max_length=10)] = None
    account_address: Optional[constr(max_length=100)] = None

    class Config:
        extra = "forbid"

class DeviceRequest(BaseModel):
    device_type: constr(min_length=3, max_length=30)  # e.g., "Arduino Uno"
    device_id: constr(pattern=r"^[A-Za-z0-9\-_]{4,40}$")  # Alphanumeric ID, allows dash/underscore
    connection_type: constr(min_length=3, max_length=20)  # e.g., "WiFi", "Zigbee"
    estate: constr(min_length=3, max_length=100)  # e.g., "Sunshine Valley Estate"
    pin_loads: List[Dict[str, str]]  # [{"pin": "D2", "load": "LED"}]

    class Config:
        extra = "forbid"  # Disallow extra fields

    @validator("pin_loads")
    def validate_pin_loads(cls, value):
        for item in value:
            if "pin" not in item or "load" not in item:
                raise ValueError("Each pin_load must have 'pin' and 'load' keys.")
            if not (1 <= len(item["pin"]) <= 5):
                raise ValueError("Pin name must be 1 to 5 characters long.")
            if not (1 <= len(item["load"]) <= 30):
                raise ValueError("Load name must be 1 to 30 characters long.")
        return value

class DeviceUpdateRequest(BaseModel):
    device_type: Optional[constr(min_length=2, max_length=50)] = Field(None, description="Type of the device (e.g., SmartMeter, Controller)")
    device_id: Optional[constr(min_length=4, max_length=40, pattern=r"^[A-Za-z0-9\-_]+$")] = Field(None, description="Unique alphanumeric device ID (allows - and _)")
    connection_type: Optional[str] = Field(None, description="How the device is connected (e.g., WiFi, GSM, LoRa)")
    estate: Optional[constr(min_length=2, max_length=100)] = Field(None, description="Estate name where the device is located")
    pin_loads: Optional[List[Dict[str, str]]] = Field(None, description="List of pin-load mappings, e.g., [{\"pin\": \"D2\", \"load\": \"LED\"}]")

    class Config:
        extra = "forbid"

class TokenPurchaseRequest(BaseModel):
    payment_tx_id: constr(min_length=5, max_length=100) = Field(..., description="Transaction ID for the payment (Mpesa or STRK)")
    payment_method: constr(min_length=2, max_length=20) = Field(..., description="Payment method used, e.g., 'strk', 'mpesa'")
    amount_sct: condecimal(gt=0) = Field(..., description="Amount of Solaris Conexus Tokens (SCT) purchased")
    strk_used: condecimal(ge=0) = Field(..., description="Amount of STRK tokens used in the transaction")
    date: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Timestamp of the token purchase")

    class Config:
        extra = "forbid"

class CreateTradeRequest(BaseModel):
    sct_offered: condecimal(gt=0)
    strk_price: condecimal(gt=0)
    tx_hash: constr(min_length=5, max_length=100)
    status: Optional[str] = "pending"
    date: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Config:
        extra = "forbid"


class CancelTradeRequest(BaseModel):
    trade_id: int
    tx_hash: constr(min_length=5, max_length=100)

    class Config:
        extra = "forbid"


class AcceptTradeRequest(BaseModel):
    trade_contract_id: int
    trade_backend_id: int
    tx_hash: constr(min_length=5, max_length=100)
    sct_offered: int  # Corrected from sct_offered if it was a typo

    class Config:
        extra = "forbid"



class STKPushRequest(BaseModel):
    amount: float

    class Config:
        extra = "forbid"




