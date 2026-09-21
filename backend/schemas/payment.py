from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..models.payment import PaymentStatus

class PaymentCreate(BaseModel):
    job_id: int

class PaymentResponse(BaseModel):
    id: int
    job_id: int
    total_amount: float
    worker_amount: float
    cooperative_amount: float
    platform_amount: float
    worker_percentage: float
    cooperative_percentage: float
    platform_percentage: float
    payment_status: PaymentStatus
    transaction_id: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class PolicyUpdate(BaseModel):
    worker_percentage: float
    cooperative_percentage: float
    platform_percentage: float
    notes: Optional[str] = None
