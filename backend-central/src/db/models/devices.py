# /src/db/models/devices.py
# SQLAlchemy models and database helper functions

from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Date, JSON
from sqlalchemy.orm import relationship, Session

from src.db.database import Base
# ============================
# Models
# ============================
class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    device_type = Column(String(50), nullable=False)
    device_id = Column(String(50), unique=True, nullable=False)
    connection_type = Column(String(50), nullable=False)
    estate = Column(String(100), ForeignKey("hubs.name"), nullable=True)
    status = Column(String(50), nullable=True)
    pin_loads = Column(JSON, nullable=True)
    created_at = Column(Date, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="devices")
    hub = relationship("Hub", back_populates="devices")

    def to_dict(self):
        return {
            "device_type": self.device_type,
            "device_id": self.device_id,
            "connection_type": self.connection_type,
            "estate": self.estate,
            "status": self.status,
            "pin_loads": self.pin_loads,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def create(cls, db: Session, device_data: dict):
        device = cls(
            device_type=device_data["device_type"],
            device_id=device_data["device_id"],
            connection_type=device_data["connection_type"],
            estate=device_data.get("estate"),
            status=device_data.get("status", "active"),
            pin_loads=device_data.get("pin_loads"),
            user_id=device_data.get("user_id")
        )
        db.add(device)
        db.commit()
        db.refresh(device)
        return device

    @classmethod
    def update(cls, db: Session, user_id: int, update_data: dict):
        try:
            device = db.query(cls).filter_by(user_id=user_id).first()
            if not device:
                raise ValueError("Device not found for the user.")

            for key, value in update_data.items():
                setattr(device, key, value)

            db.commit()
            db.refresh(device)
            return device

        except SQLAlchemyError as e:
            db.rollback()
            raise RuntimeError(f"Database update failed: {str(e)}")


