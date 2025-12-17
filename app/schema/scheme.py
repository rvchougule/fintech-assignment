from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SchemeCreate(BaseModel):
    name: str
    


class SchemeUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None


class SchemeResponse(BaseModel):
    id: int
    name: str
    parent_scheme_id: Optional[int]
    is_active: bool
    created_by: int
    created_at: datetime
    
    model_config = {
            "from_attributes": True
        }
