from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.sql import func
import enum
from ..database import Base

class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, unique=True)
    
    total_amount = Column(Float, nullable=False)
    worker_amount = Column(Float, nullable=False)
    cooperative_amount = Column(Float, nullable=False)
    platform_amount = Column(Float, nullable=False)
    
    worker_percentage = Column(Float, nullable=False)
    cooperative_percentage = Column(Float, nullable=False)
    platform_percentage = Column(Float, nullable=False)
    
    payment_status = Column(SAEnum(PaymentStatus), default=PaymentStatus.PENDING)
    transaction_id = Column(String(100), unique=True, nullable=True)
    payment_method = Column(String(50), default="UPI_MOCK")  # For demo, mock gateway
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
