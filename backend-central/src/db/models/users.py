# /src/db/models/users.py
# SQLAlchemy models and database helper functions

from sqlalchemy import Column, Integer, String, or_
from sqlalchemy.orm import relationship, Session, joinedload
from typing import Optional

from src.db.database import Base
from src.utils.auth import auth_service
from src.auth.requests import RegisterRequest

# ============================
# Models
# ============================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    profile = relationship("Profile", back_populates="user", uselist=False)
    devices = relationship("Device", back_populates="user")
    purchases = relationship("TokenPurchase", back_populates="user", cascade="all, delete-orphan")
    trade_requests = relationship("TradeRequest", foreign_keys='TradeRequest.user_id', back_populates="user")

    @classmethod
    def create(cls, db: Session, user_data: RegisterRequest):
        user = cls(
            username=user_data.username,
            email=user_data.email,
            hashed_password=auth_service.hash_password(user_data.password)
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @classmethod
    def find(cls, db: Session, username: Optional[str] = None, email: Optional[str] = None) -> Optional["User"]:
        filters = []
        if username:
            filters.append(cls.username == username)
        if email:
            filters.append(cls.email == email)

        if not filters:
            return None  # or raise ValueError("At least username or email must be provided")

        return db.query(cls).filter(or_(*filters)).first()

    @classmethod
    def find_with_profile(cls, db: Session, username: str) -> Optional["User"]:
        return (
            db.query(cls)
            .filter(cls.username == username)
            .options(joinedload(cls.profile))
            .first()
        )

