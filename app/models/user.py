from sqlalchemy import (
    Column, Integer, String, Boolean, ForeignKey,
    Float, DateTime, Enum
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)

    role_id = Column(Integer, ForeignKey("roles.id"))
    parent_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=True)
    
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # <-- renamed

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    role = relationship("Role", back_populates="users")
    
    parent = relationship("User", remote_side=[id], foreign_keys=[parent_id])
    scheme = relationship("Scheme", back_populates="users", foreign_keys=[scheme_id])
    
    creator = relationship(
        "User",
        remote_side=[id],
        foreign_keys=[created_by],
        backref="created_users"  # All users created by this user
    )
