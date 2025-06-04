# /src/db/models/trades.py
# SQLAlchemy models and database helper functions

from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime, JSON, or_
from sqlalchemy.orm import relationship, Session
from sqlalchemy.orm.attributes import flag_modified

from typing import Optional

from src.db.database import Base

# ============================
# Models
# ============================
class TradeRequest(Base):
    __tablename__ = "trade_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    sct_offered = Column(Numeric(precision=18, scale=8), nullable=False)
    strk_price = Column(Numeric(precision=18, scale=8), nullable=False)
    tx_data = Column(JSON, nullable=True)

    status = Column(String(50), default="pending")
    date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", foreign_keys=[user_id], back_populates="trade_requests")
    buyer = relationship("User", foreign_keys=[buyer_id])

    @classmethod
    def create(cls, db: Session, trade_data: dict):
        trade = cls(
            user_id=trade_data["user_id"],
            sct_offered=trade_data["sct_offered"],
            strk_price=trade_data["strk_price"],
            tx_data={"create": trade_data.get("tx_hash")},
            status=trade_data.get("status", "pending"),
            date=trade_data.get("date")
        )
        db.add(trade)
        db.commit()
        db.refresh(trade)
        return trade

    @classmethod
    def all_user_trades(cls, db: Session, user_id: int):
        return db.query(cls).filter(
            or_(cls.user_id == user_id, cls.buyer_id == user_id)
        ).order_by(cls.date.desc()).all()


    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "tx_data": self.tx_data,
            "sct_offered": str(self.sct_offered),
            "strk_price": str(self.strk_price),
            "status": self.status,
            "seller": self.user.username if self.user else None,
            "buyer": self.buyer.username if self.buyer else None
        }

    @classmethod
    def find(cls, db: Session, trade_id: int) -> Optional["TradeRequest"]:
        return db.query(cls).filter(cls.id == trade_id).first()

    def cancel(self, db: Session, tx_hash: str):
        if not self.tx_data:
            self.tx_data = {}
        self.tx_data["cancelled"] = tx_hash
        self.status = "cancelled"
        flag_modified(self, "tx_data")
        # self.date = datetime.utcnow()
        db.commit()
        db.refresh(self)

    @classmethod
    def available(cls, db: Session, user_id: int):
        return db.query(cls).filter(
            cls.status == "pending",
            cls.user_id != user_id
        ).order_by(cls.date.desc()).all()

    def accept(self, db: Session, tx_hash: str, pay_tx_hash: str, buyer_id: int):
        if not self.tx_data:
            self.tx_data = {}
        self.tx_data["accept"] = tx_hash
        self.tx_data["pay_accept"] = pay_tx_hash
        self.buyer_id = buyer_id
        flag_modified(self, "tx_data")  # Mark tx_data as modified
        self.status = "accepted"
        # self.date = datetime.utcnow()
        db.commit()
        db.refresh(self)


