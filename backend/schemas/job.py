from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from ..models.job import JobStatus, JobPriority

class JobCreate(BaseModel):
    cooperative_id: int
    service: str
    sub_service: Optional[str] = None
    description: Optional[str] = None
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    price: float
    priority: JobPriority = JobPriority.NORMAL

class JobResponse(BaseModel):
    id: int
    customer_id: int
    cooperative_id: int
    worker_id: Optional[int]
    service: str
    sub_service: Optional[str]
    description: Optional[str]
    location: str
    price: float
    status: JobStatus
    priority: JobPriority
    ai_match_score: Optional[float] = None
    ai_match_explanation: Optional[str] = None
    created_at: datetime
    accepted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class JobAccept(BaseModel):
    worker_id: int

class AIMatchRequest(BaseModel):
    job_id: int
    top_k: int = 5

class AIMatchScore(BaseModel):
    worker_id: int
    member_id: str
    name: str
    primary_skill: str
    final_score: float
    breakdown: Dict[str, float]
    explanation: str
    distance_km: Optional[float] = None

class AIMatchResponse(BaseModel):
    job_id: int
    eligible_count: int
    matches: list[AIMatchScore]
    recommended_worker_id: int
