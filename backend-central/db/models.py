# db/models.py
# This file defines the SQLAlchemy models for the database tables.
# It includes the User model and a function to create a new user.
from sqlalchemy import Column, Integer, String, ForeignKey, Date, JSON, Numeric, DateTime
from sqlalchemy.orm import relationship, Session
from db.database import Base
from auth.utils import hash_password
from auth.models import RegisterRequest
from datetime import datetime
from datetime import date
import secrets

# User Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # One-to-one relationship with Profile
    profile = relationship("Profile", back_populates="user", uselist=False)
    # One-to-many relationship with Device
    devices = relationship("Device", back_populates="user")
    # One-to-many: a user can have multiple wallets

    wallets = relationship("Wallet", back_populates="user", cascade="all, delete-orphan")

    # Inside your User model
    purchases = relationship("TokenPurchase", back_populates="user", cascade="all, delete-orphan")

    # In User model
    trade_requests = relationship("TradeRequest", foreign_keys='TradeRequest.user_id', back_populates="user")




# Profile Model
class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    dob = Column(Date, nullable=False)  # Store as a Date type now
    gender = Column(String(10), nullable=False)
    phone = Column(String(15), nullable=True)  # Optional phone number field
    account_address = Column(String(66), unique=True, nullable=False)


    # Foreign key to link to the User model
    user_id = Column(Integer, ForeignKey("users.id"))

    # Back-reference to the user
    user = relationship("User", back_populates="profile")

    # Add a method to convert the object to a dictionary
    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "dob": self.dob.isoformat() if isinstance(self.dob, date) else self.dob,  # Convert date to ISO format string
            "gender": self.gender,
            "phone": self.phone,
            "account_address": self.account_address,
        }


# Function to create a user
def create_user(db: Session, user: RegisterRequest):
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Function to create a profile for an existing user
def create_profile(db: Session, profile_data: dict):
    # Ensure that the user exists first
    user = db.query(User).filter(User.id == profile_data["user_id"]).first()
    
    if not user:
        raise ValueError("User not found")
    
    # Create the profile linked to the user
    db_profile = Profile(
        first_name=profile_data["first_name"],
        last_name=profile_data["last_name"],
        dob=profile_data["dob"],  # Expecting dob as a Date object
        gender=profile_data["gender"],
        phone=profile_data.get("phone", None),  # Optional phone number field
        account_address=profile_data.get("account_address", None),  # Optional phone number field
        user_id=user.id
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)

    return db_profile

# Device Model
class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    device_type = Column(String(50), nullable=False)  # e.g., 'Arduino', 'Raspberry Pi', etc.
    device_id = Column(String(50), nullable=False, unique=True)  # Unique identifier for each device
    connection_type = Column(String(50), nullable=False)  # e.g., 'wired', 'wireless'
    estate = Column(String(100), ForeignKey("hubs.name"), nullable=True)  # The estate where the device is located (optional)
    status = Column(String(50), nullable=True)  # e.g., 'active', 'inactive'
    pin_loads = Column(JSON, nullable=True)  # JSON array to store pin numbers and loads
    created_at = Column(Date, default=datetime.utcnow)  # Timestamp of device creation

    user_id = Column(Integer, ForeignKey("users.id"))  # Reference to the User (admin or manager)
    
    # Relationship with the User model
    user = relationship("User", back_populates="devices")

    hub = relationship("Hub", back_populates="devices")

    # Add a method to convert the object to a dictionary
    def to_dict(self):
        return {
            "id": self.id,
            "device_type": self.device_type,
            "device_id": self.device_id,
            "connection_type": self.connection_type,
            "estate": self.estate,
            "status": self.status,
            "pin_loads": self.pin_loads,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "user_id": self.user_id
        }

# Function to create a new device
def create_device(db: Session, device_data: dict, user_id: int):
    db_device = Device(
        device_type=device_data["device_type"],
        device_id=device_data["device_id"],
        connection_type=device_data["connection_type"],
        estate=device_data.get("estate"),
        status=device_data.get("status", "active"),
        pin_loads=device_data.get("pin_loads"),
        user_id=user_id  # Assign the device to the user (admin or manager)
    )

    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


class Wallet(Base):
    __tablename__ = "wallets"
    id = Column(Integer, primary_key=True, index=True)
    # Link to the User; can be null if not yet assigned
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Ethereum-style address and keys
    account_address = Column(String(66), unique=True, nullable=False)
    private_key = Column(String(66), nullable=False)
    public_key = Column(String(66), nullable=False)

    # Relationship back to User
    user = relationship("User", back_populates="wallets")

def assign_wallet_to_user(db: Session, user_id: int):
    # Check if user already has a wallet
    user_wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if user_wallet:
        print(f"User {user_id} already has a wallet assigned.")
        return user_wallet  # Return existing wallet

    # Find the first unassigned wallet
    unassigned_wallet = db.query(Wallet).filter(Wallet.user_id == None).first()
    if not unassigned_wallet:
        print("No available wallets to assign.")
        return None  # No wallet available

    # Assign the unassigned wallet to the user
    unassigned_wallet.user_id = user_id
    db.commit()
    db.refresh(unassigned_wallet)

    print(f"Assigned wallet {unassigned_wallet.account_address} to user {user_id}")
    return unassigned_wallet

class TokenPurchase(Base):
    __tablename__ = "token_purchases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    date = Column(DateTime, default=datetime.utcnow)
    tx_hash = Column(String(255), unique=True, nullable=False)
    amount_stc = Column(Numeric(precision=18, scale=8), nullable=False)
    strk_used = Column(Numeric(precision=18, scale=8), nullable=False)

    # Relationship back to user
    user = relationship("User", back_populates="purchases")

def create_token_purchase(db: Session, purchase_data: dict, user_id: int):
    db_purchase = TokenPurchase(
        user_id=user_id,
        tx_hash=purchase_data["tx_hash"],
        amount_stc=purchase_data["amount_stc"],
        strk_used=purchase_data["strk_used"],
        date=purchase_data.get("date")  # Optional; defaults to utcnow if not provided
    )

    db.add(db_purchase)
    db.commit()
    db.refresh(db_purchase)
    return db_purchase


class TradeRequest(Base):
    __tablename__ = "trade_requests"

    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # initiator of the trade
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # person who accepts trade

    stc_offered = Column(Numeric(precision=18, scale=8), nullable=False)
    strk_price = Column(Numeric(precision=18, scale=8), nullable=False)
    tx_hash = Column(String(255), unique=True, nullable=True)
    
    status = Column(String(50), default="pending")
    date = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="trade_requests")
    buyer = relationship("User", foreign_keys=[buyer_id])

def create_trade_request(db: Session, trade_data: dict, user_id: int):
    db_trade = TradeRequest(
        user_id=user_id,
        stc_offered=trade_data["stc_offered"],
        strk_price=trade_data["strk_price"],
        tx_hash=trade_data.get("tx_hash"),  # optional at creation
        status=trade_data.get("status", "pending"),
        date=trade_data.get("date")  # optional
    )

    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    return db_trade



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
        """Creates a new hub with a secure API key."""
        api_key = secrets.token_hex(32)  # 64-character secure key

        hub = cls(
            name=name,
            api_key=api_key,
            registered_at=datetime.utcnow(),
            last_active=None
        )
        db.add(hub)
        db.commit()
        db.refresh(hub)
        
        return hub

