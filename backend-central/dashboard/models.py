# dashboard/models.py
from pydantic import BaseModel, constr, condecimal
from datetime import date, datetime
from typing import Optional, List, Dict

class ProfileRequest(BaseModel):
    first_name: constr(min_length=2, max_length=50)  # First name should be between 1 and 50 characters
    last_name: constr(min_length=2, max_length=50)   # Last name should be between 1 and 50 characters
    dob: date  # Date of birth, expects a date object
    gender: constr(min_length=1, max_length=10)  # Gender can be a string like "Male" or "Female"
    phone: Optional[constr(max_length=15)] = None  # Phone number is optional, with max length of 15 characters
    account_address: Optional[constr(max_length=100)] = None  # Phone number is optional, with max length of 15 characters

    class Config:
        # Allow extra fields that aren't explicitly listed in the model
        # for cases where the request includes additional data
        extra = "forbid"

# db/models.py
# Pydantic model for incoming device registration request
class DeviceRequest(BaseModel):
    device_type: str
    device_id: str
    connection_type: str
    estate: Optional[str] = None
    #status: Optional[str] = "active"
    pin_loads: Optional[List[Dict[str, str]]] = None  # Example: [{"pin": "D2", "load": "LED"}, {"pin": "D3", "load": "Fan"}]

    class Config:
        orm_mode = True

class TokenPurchaseRequest(BaseModel):
    tx_hash: constr(min_length=5, max_length=100)
    amount_stc: condecimal(gt=0)  # Amount in STC must be a positive decimal
    strk_used: condecimal(ge=0)   # STRK used must be 0 or more
    date: Optional[datetime] = None  # Optional, defaults to now in DB if not provided

    class Config:
        orm_mode = True

class TradeRequest(BaseModel):
    stc_offered: condecimal(gt=0)
    strk_price: condecimal(gt=0)
    tx_hash: constr(min_length=5, max_length=100)
    status: Optional[str] = "pending"
    date: Optional[datetime] = None

    class Config:
        orm_mode = True

class CancelTradeRequest(BaseModel):
    trade_id: int 
    tx_hash: constr(min_length=5, max_length=100)
    class Config:
        orm_mode = True

class AcceptTradeRequest(BaseModel):
    trade_contract_id: int
    trade_backend_id: int
    tx_hash: constr(min_length=5, max_length=100)
    sct_offered: int

    class Config:
        orm_mode = True

