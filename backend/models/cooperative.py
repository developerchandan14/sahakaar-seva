from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.sql import func
from ..database import Base

class Cooperative(Base):
    __tablename__ = "cooperatives"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    registration_number = Column(String(100), unique=True, nullable=False)
    description = Column(String(500), nullable=True)
    location = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    total_members = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
