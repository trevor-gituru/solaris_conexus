# /src/db/models/hubs.py
# SQLAlchemy models and database helper functions

from datetime import datetime
import secrets

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship, Session

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
    last_active = Column(DateTime, nullable=True)

    devices = relationship("Device", back_populates="hub")

    @classmethod
    def create(cls, db: Session, name: str):
        api_key = secrets.token_hex(32)
        hub = cls(name=name, api_key=api_key)
        db.add(hub)
        db.commit()
        db.refresh(hub)
        return hub
