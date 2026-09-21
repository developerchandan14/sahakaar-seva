from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum as SAEnum, JSON
from sqlalchemy.sql import func
import enum
from ..database import Base

class VerificationStatus(str, enum.Enum):
    PENDING = "PENDING"
    UNDER_REVIEW = "UNDER_REVIEW"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"

class AvailabilityStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    BUSY = "BUSY"
    OFFLINE = "OFFLINE"
    ON_LEAVE = "ON_LEAVE"

class Worker(Base):
    __tablename__ = "workers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    cooperative_id = Column(Integer, ForeignKey("cooperatives.id"), nullable=False)
    member_id = Column(String(50), unique=True, index=True, nullable=False)  # e.g., FSWC-E-184
    
    primary_skill = Column(String(50), nullable=False, index=True)  # electrician, plumber, carpenter, cleaner
    secondary_skills = Column(JSON, default=list)  # ["wiring", "inverter"]
    
    experience_years = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    total_jobs = Column(Integer, default=0)
    completed_jobs = Column(Integer, default=0)
    cancelled_jobs = Column(Integer, default=0)
    
    availability_status = Column(SAEnum(AvailabilityStatus), default=AvailabilityStatus.AVAILABLE)
    verification_status = Column(SAEnum(VerificationStatus), default=VerificationStatus.PENDING)
    
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # For fairness tracking
    jobs_this_week = Column(Integer, default=0)
    jobs_this_month = Column(Integer, default=0)
    last_job_at = Column(DateTime(timezone=True), nullable=True)
    
    # Reliability metrics
    completion_rate = Column(Float, default=1.0)
    avg_response_time_minutes = Column(Float, default=30.0)
    
    insurance_status = Column(String(20), default="PENDING")  # ACTIVE, PENDING, EXPIRED
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
