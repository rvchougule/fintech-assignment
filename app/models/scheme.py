from sqlalchemy import UniqueConstraint
from sqlalchemy import (
    Column, Integer, String, Boolean, ForeignKey,
    Float, DateTime, Enum
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.models import RoleEnum, CommissionTypeEnum
from app.core.database import Base

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True)
    category = Column(String, nullable=False)   # Banking, BBPS
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)

    commissions = relationship("SchemeCommission", back_populates="service")


class Scheme(Base):
    __tablename__ = "schemes"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    parent_scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    parent_scheme = relationship("Scheme", remote_side=[id], backref="child_schemes")

    commissions = relationship("SchemeCommission", back_populates="scheme")

    users = relationship(
        "User",
        back_populates="scheme",
        foreign_keys="[User.scheme_id]"  # <--- Specify foreign key here
    )

