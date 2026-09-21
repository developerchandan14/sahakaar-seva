from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from ..database import get_db
from ..models.worker import Worker
from ..models.job import Job, JobStatus
from ..models.payment import Payment
from ..models.user import User
from ..models.cooperative import Cooperative
from ..schemas.cooperative import DashboardStats, CooperativeResponse
from ..routes.auth import get_current_active_user

router = APIRouter(prefix="/cooperative", tags=["Cooperative"])

@router.get("/{coop_id}", response_model=CooperativeResponse)
def get_cooperative(coop_id: int, db: Session = Depends(get_db)):
    coop = db.query(Cooperative).filter(Cooperative.id == coop_id).first()
    if not coop:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Cooperative not found")
    return coop

@router.get("/{coop_id}/dashboard")
def get_dashboard(coop_id: int, db: Session = Depends(get_db)):
    # Total workers
    total_workers = db.query(Worker).filter(Worker.cooperative_id == coop_id).count()
    
    # By skill
    skill_counts = db.query(Worker.primary_skill, func.count(Worker.id)).filter(
        Worker.cooperative_id == coop_id
    ).group_by(Worker.primary_skill).all()
    by_skill = {skill: count for skill, count in skill_counts}
    
    # Jobs today
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    todays_jobs = db.query(Job).filter(
        Job.cooperative_id == coop_id,
        Job.created_at >= today_start
    ).count()
    
    completed = db.query(Job).filter(
        Job.cooperative_id == coop_id,
        Job.status == JobStatus.COMPLETED,
        Job.created_at >= today_start
    ).count()
    
    active = db.query(Job).filter(
        Job.cooperative_id == coop_id,
        Job.status.in_([JobStatus.ACCEPTED, JobStatus.IN_PROGRESS, JobStatus.ASSIGNED, JobStatus.MATCHING])
    ).count()
    
    cancelled = db.query(Job).filter(
        Job.cooperative_id == coop_id,
        Job.status == JobStatus.CANCELLED,
        Job.created_at >= today_start
    ).count()
    
    # Revenue today
    payments_today = db.query(Payment).join(Job, Payment.job_id == Job.id).filter(
        Job.cooperative_id == coop_id,
        Payment.created_at >= today_start
    ).all()
    
    total_revenue = sum(p.total_amount for p in payments_today)
    worker_earnings = sum(p.worker_amount for p in payments_today)
    coop_earnings = sum(p.cooperative_amount for p in payments_today)
    
    # Verification pending
    verification_pending = db.query(Worker).filter(
        Worker.cooperative_id == coop_id,
        Worker.verification_status != "VERIFIED"
    ).count()
    
    # Avg jobs per worker
    workers = db.query(Worker).filter(Worker.cooperative_id == coop_id).all()
    avg_jobs = sum(w.jobs_this_week or 0 for w in workers) / len(workers) if workers else 0
    
    # Avg by skill
    avg_by_skill = {}
    for skill in by_skill.keys():
        skill_workers = [w for w in workers if w.primary_skill == skill]
        avg = sum(w.jobs_this_week or 0 for w in skill_workers) / len(skill_workers) if skill_workers else 0
        avg_by_skill[skill] = round(avg, 2)
    
    # Opportunity equity - simple calculation
    # Gini-based equity from jobs_this_week
    counts = [w.jobs_this_week or 0 for w in workers]
    if counts and sum(counts) > 0:
        # Simple equity: 100 - (std/mean * 50)
        mean = sum(counts)/len(counts)
        std = (sum((x-mean)**2 for x in counts)/len(counts))**0.5
        equity = max(0, min(100, 100 - (std/mean*50 if mean>0 else 0)))
    else:
        equity = 85
    
    return {
        "total_workers": total_workers,
        "total_customers": db.query(User).filter(User.role == "CUSTOMER").count(),
        "todays_jobs": todays_jobs,
        "completed_jobs": completed,
        "active_jobs": active,
        "cancelled_jobs": cancelled,
        "total_revenue": round(total_revenue, 2),
        "worker_earnings": round(worker_earnings, 2),
        "cooperative_earnings": round(coop_earnings, 2),
        "opportunity_equity": round(equity, 1),
        "verification_pending": verification_pending,
        "by_skill": by_skill,
        "avg_jobs_per_worker": round(avg_jobs, 2),
        "avg_jobs_by_skill": avg_by_skill
    }

@router.get("/{coop_id}/workers")
def get_coop_workers(coop_id: int, db: Session = Depends(get_db)):
    workers = db.query(Worker).filter(Worker.cooperative_id == coop_id).all()
    result = []
    for w in workers:
        user = db.query(User).filter(User.id == w.user_id).first()
        result.append({
            "id": w.id,
            "member_id": w.member_id,
            "name": user.name if user else "Unknown",
            "phone": user.phone if user else "",
            "skill": w.primary_skill,
            "rating": w.rating,
            "jobs_this_week": w.jobs_this_week,
            "jobs_this_month": w.jobs_this_month,
            "total_jobs": w.total_jobs,
            "verification_status": w.verification_status.value if hasattr(w.verification_status, 'value') else str(w.verification_status),
            "availability": w.availability_status.value if hasattr(w.availability_status, 'value') else str(w.availability_status),
            "insurance": w.insurance_status
        })
    return result

@router.get("/{coop_id}/jobs")
def get_coop_jobs(coop_id: int, limit: int = 100, db: Session = Depends(get_db)):
    jobs = db.query(Job).filter(Job.cooperative_id == coop_id).order_by(Job.created_at.desc()).limit(limit).all()
    return jobs

@router.get("/{coop_id}/analytics")
def get_analytics(coop_id: int, db: Session = Depends(get_db)):
    # Jobs by service
    by_service = db.query(Job.service, func.count(Job.id)).filter(
        Job.cooperative_id == coop_id
    ).group_by(Job.service).all()
    
    # Revenue last 7 days
    seven_days_ago = datetime.now() - timedelta(days=7)
    daily_revenue = []
    for i in range(7):
        day = datetime.now() - timedelta(days=6-i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        day_payments = db.query(Payment).join(Job, Payment.job_id == Job.id).filter(
            Job.cooperative_id == coop_id,
            Payment.created_at >= day_start,
            Payment.created_at < day_end
        ).all()
        daily_revenue.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "revenue": sum(p.total_amount for p in day_payments),
            "jobs": len(day_payments)
        })
    
    return {
        "jobs_by_service": {s: c for s, c in by_service},
        "daily_revenue": daily_revenue
    }
