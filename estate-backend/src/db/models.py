from .database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Date, JSON, Numeric, DateTime, Float, BigInteger
from sqlalchemy.orm import Session, relationship
from datetime import datetime

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True, autoincrement=False)
    device_type = Column(String(50), nullable=False)         # e.g., 'Arduino', 'Raspberry Pi'
    device_id = Column(String(50), nullable=False, unique=True)  # Unique per device
    connection_type = Column(String(50), nullable=False)     # e.g., 'wired', 'wireless'
    status = Column(String(50), nullable=True)               # e.g., 'active', 'inactive'
    pin_loads = Column(JSON, nullable=True)                  # JSON of pin numbers and loads
    instruction = Column(Integer, primary_key=True, index=True, default=1)


    account_address = Column(String(66), unique=True, nullable=False)         # e.g., '0x1sss'
    power_readings = relationship("PowerConsumption", back_populates="device", cascade="all, delete-orphan")
    token_balance = Column(BigInteger, default=0)  # Add this line


    @classmethod
    def create(cls, db: Session, device_data: dict):
        device = cls(
            device_type=device_data["device_type"],
            device_id=device_data["device_id"],
            connection_type=device_data["connection_type"],
            status=device_data.get("status", "active"),
            pin_loads=device_data.get("pin_loads"),
            account_address=device_data.get("account_address")
        )
        db.add(device)
        db.commit()
        db.refresh(device)
        return device

class PowerConsumption(Base):
    __tablename__ = "power_consumption"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    voltage = Column(Float, nullable=True)  # optional
    current = Column(Float, nullable=True)  # optional
    power = Column(Float, nullable=False)  # recommended at minimum

    device = relationship("Device", back_populates="power_readings")

    @classmethod
    def create(cls, db: Session, data: dict):
        voltage = data.get("voltage")
        current = data.get("current")
        power = data.get("power")

        # Calculate power if not provided but voltage and current are given
        if power is None and voltage is not None and current is not None:
            power = voltage * current
        elif power is None:
            raise ValueError("Power must be provided or calculable from voltage and current")

        power_record = cls(
            device_id=data["device_id"],
            power=power,
            voltage=voltage,
            current=current,
            timestamp=data.get("timestamp", datetime.utcnow())
        )
        db.add(power_record)
        db.commit()
        db.refresh(power_record)
        return power_record

    @classmethod
    def latest(cls, db: Session, device_id: int):
        return (
            db.query(cls)
            .filter(cls.device_id == device_id)
            .order_by(cls.timestamp.desc())
            .first()
        )


   
