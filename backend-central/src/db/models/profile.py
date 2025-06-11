# /src/db/models/profile.py
# SQLAlchemy models and database helper functions

from datetime import date

from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship, Session

from src.db.database import Base
from .users import User  # Needed for type check in create method

# ============================
# Models
# ============================
class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    dob = Column(Date, nullable=False)
    gender = Column(String(10), nullable=False)
    phone = Column(String(15), nullable=True)
    account_address = Column(String(66), unique=True, nullable=False) 
    phone2 = Column(String(15), nullable=True)
    notification = Column(String(10), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="profile")
    
    @classmethod
    def create(cls, db: Session, profile_data: dict):
        # Ensure the user exists first
        user = db.query(User).filter(User.id == profile_data["user_id"]).first()
        if not user:
            raise ValueError("User not found")

        profile = cls(
            first_name=profile_data["first_name"],
            last_name=profile_data["last_name"],
            dob=profile_data["dob"],  # Expecting a date object
            gender=profile_data["gender"],
            phone=profile_data.get("phone", None),
            account_address=profile_data.get("account_address", None),
            user_id=user.id
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile

    def to_dict(self):
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "dob": self.dob.isoformat() if isinstance(self.dob, date) else self.dob,
            "gender": self.gender,
            "phone": self.phone,
            "phone2": self.phone2,
            "notification": self.notification,
            "account_address": self.account_address,
        }

    @classmethod
    def update(cls, db: Session, user_id: int, update_data: dict):
        profile = db.query(cls).filter_by(user_id=user_id).first()
        if not profile:
            raise ValueError("Profile not found")

        for key, value in update_data.items():
            if hasattr(profile, key) and value is not None:
                setattr(profile, key, value)

        db.commit()
        db.refresh(profile)
        return profile

