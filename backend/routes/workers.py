from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.worker import Worker
from ..models.user import User
from ..schemas.worker import WorkerResponse, WorkerCreate, WorkerUpdate, AvailabilityUpdate
from ..routes.auth import get_current_active_user

router = APIRouter(prefix="/workers", tags=["Workers"])

@router.get("", response_model=List[WorkerResponse])
def list_workers(
    skill: str = None,
    cooperative_id: int = None,
    verification_status: str = None,
    availability: str = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(Worker)
    
    if skill:
        query = query.filter(Worker.primary_skill == skill)
    if cooperative_id:
        query = query.filter(Worker.cooperative_id == cooperative_id)
    if verification_status:
        query = query.filter(Worker.verification_status == verification_status)
    if availability:
        query = query.filter(Worker.availability_status == availability)
    
    workers = query.offset(offset).limit(limit).all()
    
    # Enrich with user data
    result = []
    for w in workers:
        user = db.query(User).filter(User.id == w.user_id).first()
        wr = WorkerResponse.model_validate(w)
        if user:
            wr.user_name = user.name
            wr.user_phone = user.phone
        result.append(wr)
    
    return result

@router.get("/{worker_id}", response_model=WorkerResponse)
def get_worker(worker_id: int, db: Session = Depends(get_db)):
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    user = db.query(User).filter(User.id == worker.user_id).first()
    wr = WorkerResponse.model_validate(worker)
    if user:
        wr.user_name = user.name
        wr.user_phone = user.phone
    return wr

@router.post("", response_model=WorkerResponse)
def create_worker(worker_data: WorkerCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    # Check user exists
    user = db.query(User).filter(User.id == worker_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate member_id
    count = db.query(Worker).filter(Worker.cooperative_id == worker_data.cooperative_id).count()
    member_id = f"FSWC-{worker_data.primary_skill[0].upper()}-{100+count+1}"
    
    worker = Worker(
        user_id=worker_data.user_id,
        cooperative_id=worker_data.cooperative_id,
        member_id=member_id,
        primary_skill=worker_data.primary_skill,
        secondary_skills=worker_data.secondary_skills,
        experience_years=worker_data.experience_years,
        latitude=worker_data.latitude,
        longitude=worker_data.longitude
    )
    db.add(worker)
    db.commit()
    db.refresh(worker)
    
    wr = WorkerResponse.model_validate(worker)
    wr.user_name = user.name
    wr.user_phone = user.phone
    return wr

@router.patch("/{worker_id}/availability")
def update_availability(worker_id: int, data: AvailabilityUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    worker.availability_status = data.availability_status
    db.commit()
    return {"message": "Availability updated", "status": data.availability_status}

@router.put("/{worker_id}", response_model=WorkerResponse)
def update_worker(worker_id: int, data: WorkerUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    if data.primary_skill is not None:
        worker.primary_skill = data.primary_skill
    if data.secondary_skills is not None:
        worker.secondary_skills = data.secondary_skills
    if data.availability_status is not None:
        worker.availability_status = data.availability_status
    if data.latitude is not None:
        worker.latitude = data.latitude
    if data.longitude is not None:
        worker.longitude = data.longitude
    
    db.commit()
    db.refresh(worker)
    
    user = db.query(User).filter(User.id == worker.user_id).first()
    wr = WorkerResponse.model_validate(worker)
    if user:
        wr.user_name = user.name
        wr.user_phone = user.phone
    return wr
