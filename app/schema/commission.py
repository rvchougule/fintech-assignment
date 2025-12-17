# app/schema/commission.py
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from app.models import CommissionTypeEnum

class CommissionSetup(BaseModel):
    scheme_id: int
    service_id: int
    commission_type: CommissionTypeEnum

    admin: Optional[float] = None
    white_label: Optional[float] = None
    master_distributor: Optional[float] = None
    distributor: Optional[float] = None
    retailer: Optional[float] = None
    customer: Optional[float] = None

class CommissionResponse(BaseModel):
    id: int
    scheme_id: int
    service_id: int

    admin: Optional[float]
    white_label: Optional[float]
    master_distributor: Optional[float]
    distributor: Optional[float]
    retailer: Optional[float]
    customer: Optional[float]

    commission_type: CommissionTypeEnum
    set_by_user_id: int

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

