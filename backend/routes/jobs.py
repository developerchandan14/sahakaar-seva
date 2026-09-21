from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..database import get_db
from ..models.job import Job, JobStatus
from ..models.worker import Worker
from ..models.user import User
from ..schemas.job import JobCreate, JobResponse, JobAccept, AIMatchRequest, AIMatchResponse
from ..services.job_assignment import FairJobAssignmentEngine
from ..services.payment_service import PaymentService
from ..services.notification_service import notification_service
from ..routes.auth import get_current_active_user

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("", response_model=JobResponse)
def create_job(job_data: JobCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    job = Job(
        customer_id=current_user.id,
        cooperative_id=job_data.cooperative_id,
        service=job_data.service,
        sub_service=job_data.sub_service,
        description=job_data.description,
        location=job_data.location,
        latitude=job_data.latitude,
        longitude=job_data.longitude,
        price=job_data.price,
        priority=job_data.priority,
        status=JobStatus.CREATED
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Notify
    notification_service.notify_job_created(current_user.id, job.id)
    
    return job

@router.get("", response_model=List[JobResponse])
def list_jobs(
    customer_id: int = None,
    worker_id: int = None,
    cooperative_id: int = None,
    status: str = None,
    service: str = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(Job)
    
    if customer_id:
        query = query.filter(Job.customer_id == customer_id)
    if worker_id:
        query = query.filter(Job.worker_id == worker_id)
    if cooperative_id:
        query = query.filter(Job.cooperative_id == cooperative_id)
    if status:
        query = query.filter(Job.status == status)
    if service:
        query = query.filter(Job.service == service)
    
    query = query.order_by(Job.created_at.desc())
    jobs = query.offset(offset).limit(limit).all()
    return jobs

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.post("/{job_id}/accept")
def accept_job(job_id: int, data: JobAccept, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status not in [JobStatus.CREATED, JobStatus.ASSIGNED, JobStatus.MATCHING]:
        raise HTTPException(status_code=400, detail=f"Job cannot be accepted in status {job.status}")
    
    worker = db.query(Worker).filter(Worker.id == data.worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    job.worker_id = data.worker_id
    job.status = JobStatus.ACCEPTED
    job.accepted_at = datetime.utcnow()
    
    # Update worker stats
    worker.jobs_this_week = (worker.jobs_this_week or 0) + 1
    worker.jobs_this_month = (worker.jobs_this_month or 0) + 1
    worker.last_job_at = datetime.utcnow()
    
    db.commit()
    
    # Create payment record
    try:
        payment = PaymentService.create_payment_for_job(db, job)
    except Exception as e:
        print(f"Payment creation failed: {e}")
    
    notification_service.notify_new_job(worker.user_id, job.id, job.service)
    
    return {"message": "Job accepted", "job_id": job.id, "worker_id": worker.id}

@router.post("/{job_id}/complete")
def complete_job(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status not in [JobStatus.ACCEPTED, JobStatus.IN_PROGRESS]:
        raise HTTPException(status_code=400, detail="Job not in progress")
    
    job.status = JobStatus.COMPLETED
    job.completed_at = datetime.utcnow()
    
    if job.worker_id:
        worker = db.query(Worker).filter(Worker.id == job.worker_id).first()
        if worker:
            worker.total_jobs = (worker.total_jobs or 0) + 1
            worker.completed_jobs = (worker.completed_jobs or 0) + 1
    
    db.commit()
    
    # Update payment status
    from ..models.payment import Payment
    payment = db.query(Payment).filter(Payment.job_id == job.id).first()
    if payment:
        payment.payment_status = "COMPLETED"
        db.commit()
        if job.worker_id:
            worker = db.query(Worker).filter(Worker.id == job.worker_id).first()
            if worker:
                notification_service.notify_payment(worker.user_id, payment.worker_amount, payment.total_amount)
    
    return {"message": "Job completed", "job_id": job.id}

@router.post("/{job_id}/cancel")
def cancel_job(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job.status = JobStatus.CANCELLED
    db.commit()
    return {"message": "Job cancelled"}

@router.post("/ai/match", response_model=AIMatchResponse)
def ai_match_worker(request: AIMatchRequest, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == request.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    engine = FairJobAssignmentEngine()
    eligible = engine.get_eligible_workers(db, job)
    
    if not eligible:
        return AIMatchResponse(
            job_id=job.id,
            eligible_count=0,
            matches=[],
            recommended_worker_id=0
        )
    
    matches = engine.find_best_workers(job, eligible, top_k=request.top_k)
    
    # Enrich with names
    enriched = []
    for m in matches:
        worker = db.query(Worker).filter(Worker.id == m['worker_id']).first()
        user = db.query(User).filter(User.id == worker.user_id).first() if worker else None
        enriched.append({
            **m,
            "name": user.name if user else f"Worker {m['worker_id']}",
            "primary_skill": worker.primary_skill if worker else "unknown"
        })
    
    # Update job with AI explanation
    if enriched:
        top = enriched[0]
        job.ai_match_score = top['final_score']
        job.ai_match_explanation = str(top['breakdown'])
        job.status = JobStatus.MATCHING
        db.commit()
    
    return AIMatchResponse(
        job_id=job.id,
        eligible_count=len(eligible),
        matches=enriched,
        recommended_worker_id=enriched[0]['worker_id'] if enriched else 0
    )
