from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum as SAEnum, Text
from sqlalchemy.sql import func
import enum
from ..database import Base

class JobStatus(str, enum.Enum):
    CREATED = "CREATED"
    MATCHING = "MATCHING"
    ASSIGNED = "ASSIGNED"
    ACCEPTED = "ACCEPTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    DISPUTED = "DISPUTED"

class JobPriority(str, enum.Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGENT"

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cooperative_id = Column(Integer, ForeignKey("cooperatives.id"), nullable=False)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=True)
    
    service = Column(String(50), nullable=False, index=True)  # electrician, plumber, etc.
    sub_service = Column(String(100), nullable=True)  # fan repair, switchboard, etc.
    description = Column(Text, nullable=True)
    
    location = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    price = Column(Float, nullable=False)
    
    status = Column(SAEnum(JobStatus), default=JobStatus.CREATED)
    priority = Column(SAEnum(JobPriority), default=JobPriority.NORMAL)
    
    # AI matching metadata (for explainability)
    ai_match_score = Column(Float, nullable=True)
    ai_match_explanation = Column(Text, nullable=True)  # JSON string
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
