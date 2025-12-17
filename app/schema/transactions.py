from pydantic import BaseModel

class TransactionCreate(BaseModel):
    service_id: int
    amount: float
