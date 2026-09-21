from sqlalchemy.orm import Session
from ..models.worker import Worker, VerificationStatus
from datetime import datetime

class VerificationService:
    @staticmethod
    def verify_worker(db: Session, worker_id: int, approved: bool, reviewer_id: int = None) -> Worker:
        worker = db.query(Worker).filter(Worker.id == worker_id).first()
        if not worker:
            raise ValueError("Worker not found")
        
        if approved:
            worker.verification_status = VerificationStatus.VERIFIED
        else:
            worker.verification_status = VerificationStatus.REJECTED
        
        db.commit()
        db.refresh(worker)
        return worker
    
    @staticmethod
    def get_pending_verifications(db: Session, cooperative_id: int):
        return db.query(Worker).filter(
            Worker.cooperative_id == cooperative_id,
            Worker.verification_status.in_([VerificationStatus.PENDING, VerificationStatus.UNDER_REVIEW])
        ).all()
