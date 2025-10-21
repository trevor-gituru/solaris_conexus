# /src/db/models/power

from src.db.database import Base  
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float
from sqlalchemy.orm import Session, relationship
from datetime import datetime

class PowerConsumption(Base):
    __tablename__ = "power_consumption"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    voltage = Column(Float, nullable=True)
    current = Column(Float, nullable=True)
    power = Column(Float, nullable=False)

    device = relationship("Device", back_populates="power_readings")

    def __repr__(self):
        return f"<PowerConsumption device_id={self.device_id} power={self.power} timestamp={self.timestamp}>"

    @classmethod
    def create(cls, db: Session, data: dict):
        voltage = data.get("voltage")
        current = data.get("current")
        power = data.get("power")

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

