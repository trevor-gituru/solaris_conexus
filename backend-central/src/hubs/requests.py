# src/hubs/requests.py
from pydantic import BaseModel, constr

 
class HubCreateRequest(BaseModel):
    name: constr(min_length=1, max_length=50)

    class Config:
        # Allow extra fields that aren't explicitly listed in the model
        # for cases where the request includes additional data
        extra = "forbid"

class DeviceRequest(BaseModel):
    device_id: constr(min_length=1, max_length=50)

    class Config:
        # Allow extra fields that aren't explicitly listed in the model
        # for cases where the request includes additional data
        extra = "forbid"

class TokenConsumptionRequest(BaseModel):
    device_id: constr(min_length=1, max_length=50)
    tx_hash: constr(min_length=5, max_length=100)
    balance: int 

    class Config:
        # Allow extra fields that aren't explicitly listed in the model
        # for cases where the request includes additional data
        extra = "forbid"
