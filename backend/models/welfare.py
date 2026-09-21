from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, JSON
from sqlalchemy.sql import func
from ..database import Base

class Welfare(Base):
    __tablename__ = "welfares"
    
    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False, unique=True)
    
    insurance_status = Column(String(20), default="PENDING")  # ACTIVE, PENDING, EXPIRED
    insurance_amount = Column(Float, default=200000.0)  # 2L default
    insurance_provider = Column(String(100), default="Cooperative Welfare Fund")
    
    benefits = Column(JSON, default=dict)  # {"health": true, "accident": true, "training_subsidy": true}
    
    total_earnings = Column(Float, default=0.0)
    total_cooperative_contribution = Column(Float, default=0.0)
    
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
