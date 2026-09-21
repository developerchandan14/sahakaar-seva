from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func
from ..database import Base

class Training(Base):
    __tablename__ = "trainings"
    
    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    
    course = Column(String(150), nullable=False)
    skill = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    
    status = Column(String(20), default="RECOMMENDED")  # RECOMMENDED, ENROLLED, IN_PROGRESS, COMPLETED
    recommended_by_ai = Column(Boolean, default=False)
    ai_reason = Column(String(500), nullable=True)
    
    recommended_at = Column(DateTime(timezone=True), server_default=func.now())
    completion_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
