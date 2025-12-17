# app/models/commission.py
from sqlalchemy import (
    Column, Integer, ForeignKey, Float,
    DateTime, Enum, UniqueConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
from app.models.models import RoleEnum, CommissionTypeEnum


class SchemeCommission(Base):
    __tablename__ = "scheme_commissions"

    id = Column(Integer, primary_key=True)

    scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)

    # Absolute MAX commission allowed at each role
    admin = Column(Float)
    white_label = Column(Float)
    master_distributor = Column(Float)
    distributor = Column(Float)
    retailer = Column(Float)
    customer = Column(Float)

    commission_type = Column(Enum(CommissionTypeEnum), nullable=False)

    set_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    scheme = relationship("Scheme", back_populates="commissions")
    service = relationship("Service", back_populates="commissions")
    set_by = relationship("User")

    __table_args__ = (
        UniqueConstraint(
            "scheme_id",
            "service_id",
            name="uq_scheme_service"
        ),
    )
