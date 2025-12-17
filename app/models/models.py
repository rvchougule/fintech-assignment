from sqlalchemy import (
    Column, Integer, String, Boolean, ForeignKey,
    Float, DateTime, Enum
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base

class RoleEnum(str, enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    WHITE_LABEL="WHITE_LABEL"
    MASTER_DISTRIBUTOR = "MASTER_DISTRIBUTOR"
    DISTRIBUTOR = "DISTRIBUTOR"
    RETAILER = "RETAILER"
    CUSTOMER = "CUSTOMER"


class CommissionTypeEnum(str, enum.Enum):
    PERCENTAGE = "PERCENTAGE"
    FLAT = "FLAT"


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(Enum(RoleEnum), unique=True, nullable=False)
    level = Column(Integer, nullable=False)

    users = relationship("User", back_populates="role")
