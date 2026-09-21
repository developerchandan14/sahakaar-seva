from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.payment import Payment
from ..models.job import Job
from ..schemas.payment import PaymentResponse, PolicyUpdate
from ..services.payment_service import PaymentService
from ..models.policy import CooperativePolicy
from ..models.user import User
from ..routes.auth import get_current_active_user

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/create", response_model=PaymentResponse)
def create_payment(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    existing = db.query(Payment).filter(Payment.job_id == job_id).first()
    if existing:
        return existing
    
    payment = PaymentService.create_payment_for_job(db, job)
    return payment

@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.get("/job/{job_id}", response_model=PaymentResponse)
def get_payment_by_job(job_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.job_id == job_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found for job")
    return payment

@router.get("/job/{job_id}/transparency")
def get_transparency(job_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.job_id == job_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return PaymentService.get_transparency_message(payment)

@router.get("/cooperative/{coop_id}/policy")
def get_policy(coop_id: int, db: Session = Depends(get_db)):
    policy = PaymentService.get_active_policy(db, coop_id)
    return policy

@router.put("/cooperative/{coop_id}/policy")
def update_policy(coop_id: int, data: PolicyUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    if not PaymentService.validate_percentages(data.worker_percentage, data.cooperative_percentage, data.platform_percentage):
        raise HTTPException(status_code=400, detail="Percentages must sum to 100 and worker >=50%")
    
    # Deactivate old policies
    old_policies = db.query(CooperativePolicy).filter(
        CooperativePolicy.cooperative_id == coop_id,
        CooperativePolicy.is_active == "true"
    ).all()
    for p in old_policies:
        p.is_active = "false"
    
    new_policy = CooperativePolicy(
        cooperative_id=coop_id,
        worker_percentage=data.worker_percentage,
        cooperative_percentage=data.cooperative_percentage,
        platform_percentage=data.platform_percentage,
        approved_by=current_user.id,
        notes=data.notes or "Updated via API"
    )
    db.add(new_policy)
    db.commit()
    db.refresh(new_policy)
    return new_policy
