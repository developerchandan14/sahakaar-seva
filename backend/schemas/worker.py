from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from ..models.worker import VerificationStatus, AvailabilityStatus

class WorkerCreate(BaseModel):
    user_id: int
    cooperative_id: int
    primary_skill: str
    secondary_skills: List[str] = []
    experience_years: int = 0
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class WorkerUpdate(BaseModel):
    primary_skill: Optional[str] = None
    secondary_skills: Optional[List[str]] = None
    availability_status: Optional[AvailabilityStatus] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class WorkerResponse(BaseModel):
    id: int
    user_id: int
    cooperative_id: int
    member_id: str
    primary_skill: str
    secondary_skills: List[str]
    experience_years: int
    rating: float
    total_jobs: int
    completed_jobs: int
    availability_status: AvailabilityStatus
    verification_status: VerificationStatus
    jobs_this_week: int
    jobs_this_month: int
    completion_rate: float
    insurance_status: str
    created_at: datetime
    # Joined user info
    user_name: Optional[str] = None
    user_phone: Optional[str] = None
    
    class Config:
        from_attributes = True

class AvailabilityUpdate(BaseModel):
    availability_status: AvailabilityStatus
