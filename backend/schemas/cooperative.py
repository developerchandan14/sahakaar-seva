from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CooperativeCreate(BaseModel):
    name: str
    registration_number: str
    description: Optional[str] = None
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class CooperativeResponse(BaseModel):
    id: int
    name: str
    registration_number: str
    description: Optional[str]
    location: str
    total_members: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_workers: int
    total_customers: int
    todays_jobs: int
    completed_jobs: int
    active_jobs: int
    cancelled_jobs: int
    total_revenue: float
    worker_earnings: float
    cooperative_earnings: float
    opportunity_equity: float
    verification_pending: int
    by_skill: dict
    avg_jobs_per_worker: float
    avg_jobs_by_skill: dict

class DemandForecastItem(BaseModel):
    service: str
    current_avg: float
    forecast_next_7_days: float
    change_percent: float
    recommendation: str

class TrainingGap(BaseModel):
    skill: str
    current_trained: int
    required: int
    shortage: int
    demand_increase_percent: float
    recommended_action: str
