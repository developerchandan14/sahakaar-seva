from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.training import Training
from ..models.worker import Worker
from ..models.user import User
from ..routes.auth import get_current_active_user

router = APIRouter(prefix="/training", tags=["Training"])

@router.get("", response_model=List[dict])
def list_trainings(worker_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Training)
    if worker_id:
        query = query.filter(Training.worker_id == worker_id)
    trainings = query.all()
    return [
        {
            "id": t.id,
            "worker_id": t.worker_id,
            "course": t.course,
            "skill": t.skill,
            "status": t.status,
            "recommended_by_ai": t.recommended_by_ai,
            "ai_reason": t.ai_reason
        } for t in trainings
    ]

@router.get("/recommendations")
def get_recommendations(worker_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Training).filter(Training.status == "RECOMMENDED")
    if worker_id:
        query = query.filter(Training.worker_id == worker_id)
    recs = query.all()
    return [
        {
            "id": r.id,
            "worker_id": r.worker_id,
            "course": r.course,
            "skill": r.skill,
            "reason": r.ai_reason,
            "recommended_by_ai": r.recommended_by_ai
        } for r in recs
    ]

@router.post("/enroll")
def enroll_training(worker_id: int, course: str, skill: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    training = Training(
        worker_id=worker_id,
        course=course,
        skill=skill,
        status="ENROLLED",
        recommended_by_ai=False
    )
    db.add(training)
    db.commit()
    return {"message": "Enrolled", "training_id": training.id}

@router.patch("/{training_id}")
def update_training(training_id: int, status: str, db: Session = Depends(get_db)):
    training = db.query(Training).filter(Training.id == training_id).first()
    if not training:
        raise HTTPException(status_code=404, detail="Training not found")
    training.status = status
    db.commit()
    return {"message": "Updated", "status": status}
