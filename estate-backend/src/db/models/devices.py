# /src/db/models/devices
from src.db.database import Base
from src.utils.helpers import normalize_addr 
from sqlalchemy import Column, Integer, String, BigInteger, or_
from sqlalchemy.orm import Session, relationship
from typing import Optional

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True, autoincrement=False)
    device_id = Column(String(50), nullable=False, unique=True)  # Unique per device
    connection_type = Column(String(50), nullable=False)     # e.g., 'Producer', 'Consumer'
    status = Column(String(50), nullable=False)               # e.g., 'active', 'inactive'
    instruction = Column(Integer, default=1)
    account_address = Column(String(66), unique=True, nullable=False)         # e.g., '0x1sss'
    token_balance = Column(BigInteger, default=0, nullable=False)  # Add this line

    power_readings = relationship("PowerConsumption", back_populates="device", cascade="all, delete-orphan")


    @classmethod
    def create(cls, db: Session, device_data: dict):
        device = cls(
            id=device_data["id"],
            device_id=device_data["device_id"],
            connection_type=device_data["connection_type"],
            status="inactive",
            instruction=1,
            account_address=normalize_addr(device_data.get("account_address")),
            token_balance=device_data.get("token_balance", 0)
        )
        db.add(device)
        db.commit()
        db.refresh(device)
        return device

    @classmethod
    def find(cls, db: Session, id: Optional[str] = None, device_id: Optional[str] = None, account_address: Optional[str] = None) -> Optional["Device"]:
        filters = []
        if id:
            filters.append(cls.id == id)
        if device_id:
            filters.append(cls.device_id == device_id)
        if account_address:
            filters.append(cls.account_address == normalize_addr(account_address))

        if not filters:
            return None  

        return db.query(cls).filter(or_(*filters)).first()

    def update(self, db: Session, update_data: dict):
        for key, value in update_data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.commit()
        db.refresh(self)
        return self
    
    


    @classmethod
    def sync(cls, db: Session, device_data: dict):
        device = cls.find(db, id=device_data["id"])
        if device:
            # Update with relevant fields from device_data
            update_fields = {
                "connection_type": device_data.get("connection_type", device.connection_type),
                "device_id": device_data.get("device_id", device.device_id),
                "status": "inactive",
                "instruction": 1,
                "account_address": normalize_addr(device_data.get("account_address", device.account_address)),
                "token_balance": device_data.get("token_balance", device.token_balance),
            }
            return device.update(db, update_fields)
        else:
            return cls.create(db, device_data)

    @classmethod
    def set_all_inactive(cls, db: Session):
        db.query(cls).update({cls.status: "inactive"})
        db.commit()

    @classmethod
    def from_transfer_event(cls, db: Session, addresses: list[str, str]):
        device_list = []
        for addr in addresses:
            device = cls.find(db, account_address=addr)
            if device:
                device_list.append(device)
        return device_list


    # @classmethod
    # async def update_balances(cls, db: Session, devices_list):
    #     """
    #     Update token_balance for devices based on list of devices.
    #     Expects list of Devices like: 
    #     """
    #     addresses = [[d.account_address, d.device_id] for d in devices_list]
    #     balances = await sct_client.get_balances(addresses)
    #     for device in devices_list:
    #         token_balance = balances.get(device.account_address)
    #         device.update({"token_balance", token_balance})



