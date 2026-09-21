from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..ml.demand_forecasting import DemandForecaster, demo_forecast
from ..ml.fairness_engine import FairnessEngine, demo_fairness
from ..ml.training_recommendation import TrainingRecommender, demo_training_recommendations
from ..ml.anomaly_detection import AnomalyDetector, demo_anomalies
from ..models.job import Job
from ..models.worker import Worker
from ..models.payment import Payment
import pandas as pd

router = APIRouter(prefix="/ai", tags=["AI Intelligence"])

@router.get("/demand-forecast")
def demand_forecast(db: Session = Depends(get_db)):
    # Try to get real data, fallback to demo
    jobs = db.query(Job).all()
    if len(jobs) < 50:
        return demo_forecast()
    
    # Convert to DataFrame
    jobs_data = [{
        "service": j.service,
        "created_at": j.created_at,
        "price": j.price,
        "status": j.status.value if hasattr(j.status, 'value') else str(j.status)
    } for j in jobs]
    
    df = pd.DataFrame(jobs_data)
    forecaster = DemandForecaster()
    forecasts = forecaster.forecast_all(df)
    insights = forecaster.get_cooperative_insights(forecasts)
    
    return {
        "forecasts": forecasts,
        "insights": insights,
        "data_source": "real" if len(jobs) >= 100 else "mixed"
    }

@router.get("/workforce-insights")
def workforce_insights(db: Session = Depends(get_db)):
    workers = db.query(Worker).all()
    jobs = db.query(Job).all()
    
    if len(workers) < 10 or len(jobs) < 20:
        return demo_fairness()
    
    workers_data = [{
        "id": w.id,
        "primary_skill": w.primary_skill,
        "secondary_skills": w.secondary_skills or [],
        "jobs_this_week": w.jobs_this_week or 0,
        "jobs_this_month": w.jobs_this_month or 0,
        "total_jobs": w.total_jobs or 0,
        "member_id": w.member_id,
        "rating": w.rating or 0
    } for w in workers]
    
    jobs_data = [{
        "worker_id": j.worker_id,
        "service": j.service,
        "status": j.status.value if hasattr(j.status, 'value') else str(j.status)
    } for j in jobs]
    
    import pandas as pd
    w_df = pd.DataFrame(workers_data)
    j_df = pd.DataFrame(jobs_data)
    
    engine = FairnessEngine()
    result = engine.calculate_opportunity_equity(w_df, j_df)
    result['recommendations'] = engine.get_recommendations(result)
    return result

@router.get("/training-recommendations")
def training_recommendations(db: Session = Depends(get_db)):
    jobs = db.query(Job).all()
    if len(jobs) < 30:
        return demo_training_recommendations()
    
    # Use demo for now as it already uses forecaster
    return demo_training_recommendations()

@router.get("/anomalies")
def anomalies(db: Session = Depends(get_db)):
    workers = db.query(Worker).all()
    jobs = db.query(Job).all()
    payments = db.query(Payment).all()
    
    if len(workers) < 10:
        return demo_anomalies()
    
    import pandas as pd
    workers_data = [{
        "id": w.id,
        "member_id": w.member_id,
        "primary_skill": w.primary_skill,
        "secondary_skills": w.secondary_skills or [],
        "jobs_this_week": w.jobs_this_week or 0,
        "jobs_this_month": w.jobs_this_month or 0,
        "total_jobs": w.total_jobs or 0,
        "rating": w.rating or 4.5,
        "completion_rate": w.completion_rate or 1.0,
        "experience_years": w.experience_years or 5
    } for w in workers]
    
    jobs_data = [{
        "id": j.id,
        "worker_id": j.worker_id,
        "customer_id": j.customer_id,
        "service": j.service,
        "price": j.price,
        "status": j.status.value if hasattr(j.status, 'value') else str(j.status)
    } for j in jobs]
    
    payments_data = [{
        "job_id": p.job_id,
        "total_amount": p.total_amount
    } for p in payments] if payments else []
    
    w_df = pd.DataFrame(workers_data)
    j_df = pd.DataFrame(jobs_data)
    p_df = pd.DataFrame(payments_data) if payments_data else pd.DataFrame()
    
    detector = AnomalyDetector(contamination=0.05)
    worker_anomalies = detector.detect_worker_anomalies(w_df, j_df, p_df)
    job_anomalies = detector.detect_job_anomalies(j_df)
    
    return {
        "worker_anomalies": worker_anomalies,
        "job_anomalies": job_anomalies,
        "total_flagged": len(worker_anomalies) + len(job_anomalies),
        "note": "Flags are for review, not accusation"
    }

@router.post("/natural-language")
def natural_language_assistant(query: str, cooperative_id: int = 1):
    """
    Optional Natural Language Customer Assistant
    Converts Hindi/English mixed query to structured service request
    Prototype - keyword based, not LLM
    """
    q_lower = query.lower()
    
    services_detected = []
    urgency = "normal"
    
    # Keyword mapping
    keywords = {
        "electrician": ["fan", "switchboard", "light", "wiring", "inverter", "bijli", "current", "switch", "board", "pankha"],
        "plumber": ["pipe", "leak", "nal", "paani", "toilet", "bathroom", "tap", "drain"],
        "carpenter": ["door", "furniture", "darwaza", "almirah", "table", "chair", "wardrobe"],
        "cleaner": ["clean", "safai", "gand", "dust", "kitchen", "bathroom cleaning"]
    }
    
    for service, words in keywords.items():
        for word in words:
            if word in q_lower:
                if service not in services_detected:
                    services_detected.append(service)
                break
    
    if not services_detected:
        services_detected = ["electrician"]  # default
    
    if any(w in q_lower for w in ["urgent", "jaldi", "emergency", "abhi"]):
        urgency = "urgent"
    elif any(w in q_lower for w in ["kal", "tomorrow"]):
        urgency = "low"
    
    # Estimate price
    price_map = {"electrician": 500, "plumber": 400, "carpenter": 600, "cleaner": 800}
    estimated_price = sum(price_map.get(s, 500) for s in services_detected)
    
    return {
        "original_query": query,
        "detected_services": services_detected,
        "sub_services": [f"{s} repair" for s in services_detected],
        "urgency": urgency,
        "estimated_price": estimated_price,
        "structured": {
            "services": services_detected,
            "urgency": urgency,
            "description": query
        },
        "next_step": f"Finding verified {', '.join(services_detected)} from cooperative",
        "note": "Prototype NLP - keyword based. Production can use Indic LLM."
    }
