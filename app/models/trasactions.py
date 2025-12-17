from sqlalchemy import (
    Column, Integer, String, Boolean, ForeignKey,
    Float, DateTime, Enum
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base
from app.models.models import RoleEnum, CommissionTypeEnum

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)

    amount = Column(Float, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    scheme = relationship("Scheme")
    service = relationship("Service")


class CommissionLedger(Base):
    __tablename__ = "commission_ledger"

    id = Column(Integer, primary_key=True)

    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    role = Column(Enum(RoleEnum), nullable=False)

    scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)

    commission_type = Column(Enum(CommissionTypeEnum), nullable=False)
    commission_percent = Column(Float, nullable=False)
    commission_amount = Column(Float, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    transaction = relationship("Transaction")
    user = relationship("User")
    scheme = relationship("Scheme")
    service = relationship("Service")

