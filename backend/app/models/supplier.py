from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    phone_whatsapp = Column(String(50), nullable=True)
    payment_terms_days = Column(Integer, default=0, nullable=False)  # 0 = Cash, 7/14/30 = Tempo
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    purchases = relationship("InventoryPurchase", back_populates="supplier")

    def __repr__(self):
        return f"<Supplier(id={self.id}, name='{self.name}', terms={self.payment_terms_days})>"

    @property
    def is_credit(self) -> bool:
        return self.payment_terms_days > 0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "phone_whatsapp": self.phone_whatsapp,
            "payment_terms_days": self.payment_terms_days,
            "is_credit": self.is_credit,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }