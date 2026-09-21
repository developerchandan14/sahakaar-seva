from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from ..database import Base

class CooperativePolicy(Base):
    __tablename__ = "cooperative_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    cooperative_id = Column(Integer, ForeignKey("cooperatives.id"), nullable=False)
    
    worker_percentage = Column(Float, nullable=False, default=88.0)
    cooperative_percentage = Column(Float, nullable=False, default=6.0)
    platform_percentage = Column(Float, nullable=False, default=6.0)
    
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    effective_from = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(String(10), default="true")
    
    notes = Column(String(500), nullable=True)
