# /src/db/models/token_purchase.py

from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import relationship, Session
from decimal import Decimal

from src.db.database import Base

# ============================
# Models
# ============================
class TokenPurchase(Base):
    __tablename__ = "token_purchases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)

    # Updated field names
    sct_tx_hash = Column(String(255), unique=True, nullable=False)
    amount_sct = Column(Numeric(precision=18, scale=8), nullable=False)
    strk_used = Column(Numeric(precision=18, scale=8), nullable=False)
    payment_tx_id = Column(String(255), nullable=False)
    payment_method = Column(String(20), nullable=False, default="strk")  # e.g., "strk" or "mpesa"

    user = relationship("User", back_populates="purchases")

    @classmethod
    def create(cls, db: Session, purchase_data: dict):
        # Attempt to create and commit new purchase
        purchase = cls(
            user_id=purchase_data["user_id"],
            sct_tx_hash=purchase_data["sct_tx_hash"],
            amount_sct=purchase_data["amount_sct"],
            strk_used=purchase_data["strk_used"],
            payment_tx_id=purchase_data["payment_tx_id"],
            payment_method=purchase_data["payment_method"],
            date=purchase_data.get("date")
        )
        db.add(purchase)
        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise Exception(f"Database integrity error: {str(e)}")

        db.refresh(purchase)
        return purchase

    def to_dict(self) -> dict:
        return {
            "date": self.date.isoformat() if self.date else None,
            "sct_tx_hash": self.sct_tx_hash,
            "amount_sct": float(self.amount_sct) if isinstance(self.amount_sct, Decimal) else self.amount_sct,
            "strk_used": float(self.strk_used) if isinstance(self.strk_used, Decimal) else self.strk_used,
            "payment_tx_id": self.payment_tx_id,
            "payment_method": self.payment_method
        }

    @classmethod
    def payment_exists(cls, db: Session, payment_tx_id: str) -> bool:
        existing = db.query(cls).filter(
            (cls.payment_tx_id == payment_tx_id)
        ).first()
        return existing is not None

