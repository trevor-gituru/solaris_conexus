# /src/db/models/hubs.py
# SQLAlchemy models and database helper functions

from datetime import datetime, timedelta
import secrets

from sqlalchemy import Column, Integer, String, DateTime, or_
from sqlalchemy.orm import relationship, Session
from typing import Optional

from src.db.database import Base

# ============================
# Models
# ============================
class Hub(Base):
    __tablename__ = "hubs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    api_key = Column(String(64), unique=True, nullable=False, index=True)
    registered_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Integer, default=0, nullable=False)  # 0: inactive, 1: active

    devices = relationship("Device", back_populates="hub")

    @classmethod
    def create(cls, db: Session, name: str):
        api_key = secrets.token_hex(32)
        hub = cls(name=name, api_key=api_key)
        db.add(hub)
        db.commit()
        db.refresh(hub)
        return hub

    @classmethod
    def find(cls, db: Session, name: Optional[str] = None, api_key: Optional[str] = None) -> Optional["Hub"]:
        filters = []
        if name:
            filters.append(cls.name == name)
        if api_key:
            filters.append(cls.api_key == api_key)

        if not filters:
            return None  # or raise ValueError("At least username or email must be provided")

        return db.query(cls).filter(or_(*filters)).first()


    @classmethod
    def connect(cls, db: Session, api_key: str = None) -> Optional["Hub"]:
        hub = cls.find(db, api_key=api_key) 
        if hub:
            hub.status = 1
            db.commit()
            db.refresh(hub)

        return hub

    @classmethod
    def close(cls, db: Session, name: str) -> Optional["Hub"]:
        hub = db.query(cls).filter(cls.name == name).first()
        if hub:
            hub.status = 0
            db.commit()
            db.refresh(hub)

        return hub


    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "api_key": self.api_key,
            "registered_at": self.registered_at.isoformat(),
            "last_active": self.last_active.isoformat() if self.last_active else None
        }
