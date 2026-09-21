"""
Fair AI Job Allocation - The most important AI feature
Prevents highest-rated worker from getting all jobs
Considers: skill, availability, distance, experience, rating, reliability, workload, fairness
"""
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from ..models.worker import Worker
from ..models.job import Job
import math
import json

# Configurable weights - can be tuned per cooperative
DEFAULT_WEIGHTS = {
    "skill_match": 0.30,
    "availability": 0.15,
    "distance": 0.10,
    "experience": 0.10,
    "rating": 0.10,
    "reliability": 0.10,
    "workload_balance": 0.10,
    "fairness": 0.05
}

class FairJobAssignmentEngine:
    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or DEFAULT_WEIGHTS
        # Validate weights sum to 1
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
    
    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance in km between two points"""
        if None in [lat1, lon1, lat2, lon2]:
            return 5.0  # default distance if unknown
        
        R = 6371  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
    
    def calculate_skill_match(self, worker: Worker, job: Job) -> float:
        """0-100 score"""
        if worker.primary_skill.lower() == job.service.lower():
            base = 90.0
            # Bonus if sub-service in secondary skills
            if job.sub_service and worker.secondary_skills:
                for skill in worker.secondary_skills:
                    if job.sub_service.lower() in skill.lower() or skill.lower() in job.sub_service.lower():
                        base = 100.0
                        break
            return base
        # Secondary skill match
        if worker.secondary_skills:
            for skill in worker.secondary_skills:
                if job.service.lower() in skill.lower():
                    return 60.0
        return 20.0
    
    def calculate_availability(self, worker: Worker) -> float:
        mapping = {
            "AVAILABLE": 100.0,
            "BUSY": 30.0,
            "OFFLINE": 0.0,
            "ON_LEAVE": 0.0
        }
        return mapping.get(worker.availability_status.value if hasattr(worker.availability_status, 'value') else str(worker.availability_status), 50.0)
    
    def calculate_distance_score(self, worker: Worker, job: Job) -> Tuple[float, float]:
        distance = self.haversine_distance(
            worker.latitude, worker.longitude,
            job.latitude, job.longitude
        )
        # Closer is better: 0km=100, 5km=80, 10km=60, 20km=30, 50km+=10
        if distance <= 2:
            score = 100.0
        elif distance <= 5:
            score = 90.0
        elif distance <= 10:
            score = 70.0
        elif distance <= 20:
            score = 50.0
        else:
            score = 20.0
        return score, distance
    
    def calculate_experience_score(self, worker: Worker) -> float:
        # 0 yrs=40, 5 yrs=70, 10 yrs=90, 15+ yrs=100
        exp = worker.experience_years or 0
        if exp >= 15:
            return 100.0
        elif exp >= 10:
            return 90.0
        elif exp >= 5:
            return 70.0 + (exp-5)*4
        else:
            return 40.0 + exp*6
    
    def calculate_rating_score(self, worker: Worker) -> float:
        # Rating 0-5 scaled to 0-100
        return (worker.rating or 0) * 20.0
    
    def calculate_reliability(self, worker: Worker) -> float:
        # Based on completion_rate and response time
        completion = (worker.completion_rate or 1.0) * 100
        # Response time: <15min=100, <30=90, <60=70, >60=50
        rt = worker.avg_response_time_minutes or 30
        if rt <= 15:
            rt_score = 100
        elif rt <= 30:
            rt_score = 90
        elif rt <= 60:
            rt_score = 70
        else:
            rt_score = 50
        return (completion * 0.7 + rt_score * 0.3)
    
    def calculate_workload_balance(self, worker: Worker, all_workers: List[Worker]) -> float:
        """Lower current workload = higher score (to balance)"""
        if not all_workers:
            return 100.0
        
        # Get avg jobs this week
        avg_jobs = sum(w.jobs_this_week or 0 for w in all_workers) / len(all_workers) if all_workers else 0
        worker_jobs = worker.jobs_this_week or 0
        
        # If worker has less than avg, boost score
        # If worker has more than avg, reduce score
        if avg_jobs == 0:
            return 100.0
        
        # worker with 0 jobs when avg is 4 gets 100, worker with 8 jobs when avg 4 gets 30
        diff = worker_jobs - avg_jobs
        # Normalize: -avg => 100, 0 => 80, +avg => 40, +2*avg => 10
        if diff <= -avg_jobs:
            return 100.0
        elif diff <= 0:
            # -avg to 0 maps to 100 to 80
            return 80 + (abs(diff) / avg_jobs) * 20 if avg_jobs > 0 else 80
        else:
            # 0 to +2*avg maps to 80 to 10
            if diff >= 2*avg_jobs:
                return 10.0
            return 80 - (diff / (2*avg_jobs)) * 70
    
    def calculate_fairness(self, worker: Worker, all_workers: List[Worker]) -> float:
        """Opportunity fairness - workers with fewer total jobs get boost"""
        if not all_workers:
            return 100.0
        
        avg_total = sum(w.total_jobs or 0 for w in all_workers) / len(all_workers) if all_workers else 0
        worker_total = worker.total_jobs or 0
        
        if avg_total == 0:
            return 100.0
        
        # Similar logic to workload but based on total jobs
        diff = worker_total - avg_total
        if diff <= -avg_total*0.5:
            return 100.0  # significantly under-allocated
        elif diff <= 0:
            return 85 + (abs(diff) / (avg_total*0.5)) * 15 if avg_total > 0 else 85
        else:
            if diff >= avg_total:
                return 40.0
            return 85 - (diff / avg_total) * 45
    
    def score_worker(self, worker: Worker, job: Job, all_workers: List[Worker]) -> Dict:
        skill = self.calculate_skill_match(worker, job)
        availability = self.calculate_availability(worker)
        distance_score, distance_km = self.calculate_distance_score(worker, job)
        experience = self.calculate_experience_score(worker)
        rating = self.calculate_rating_score(worker)
        reliability = self.calculate_reliability(worker)
        workload = self.calculate_workload_balance(worker, all_workers)
        fairness = self.calculate_fairness(worker, all_workers)
        
        final = (
            skill * self.weights["skill_match"] +
            availability * self.weights["availability"] +
            distance_score * self.weights["distance"] +
            experience * self.weights["experience"] +
            rating * self.weights["rating"] +
            reliability * self.weights["reliability"] +
            workload * self.weights["workload_balance"] +
            fairness * self.weights["fairness"]
        )
        
        return {
            "worker_id": worker.id,
            "member_id": worker.member_id,
            "final_score": round(final, 2),
            "breakdown": {
                "skill_match": round(skill, 1),
                "availability": round(availability, 1),
                "distance": round(distance_score, 1),
                "experience": round(experience, 1),
                "rating": round(rating, 1),
                "reliability": round(reliability, 1),
                "workload_balance": round(workload, 1),
                "fairness": round(fairness, 1)
            },
            "distance_km": round(distance_km, 2),
            "explanation": self.generate_explanation(skill, availability, distance_score, workload, fairness, distance_km)
        }
    
    def generate_explanation(self, skill, availability, distance_score, workload, fairness, distance_km) -> str:
        parts = []
        if skill >= 90:
            parts.append("High skill match")
        elif skill >= 60:
            parts.append("Moderate skill match")
        else:
            parts.append("Low skill match")
        
        if availability == 100:
            parts.append("Available now")
        
        if distance_km <= 5:
            parts.append(f"Nearby ({distance_km}km)")
        
        if workload >= 80:
            parts.append("Low current workload - opportunity balancing")
        elif workload <= 40:
            parts.append("High workload - may need rest")
        
        if fairness >= 85:
            parts.append("High fairness score - under-allocated recently")
        
        return " • ".join(parts)
    
    def find_best_workers(self, job: Job, eligible_workers: List[Worker], top_k: int = 5) -> List[Dict]:
        if not eligible_workers:
            return []
        
        scored = [self.score_worker(w, job, eligible_workers) for w in eligible_workers]
        scored.sort(key=lambda x: x["final_score"], reverse=True)
        return scored[:top_k]
    
    def get_eligible_workers(self, db: Session, job: Job) -> List[Worker]:
        """Get workers who can do this job"""
        query = db.query(Worker).filter(
            Worker.cooperative_id == job.cooperative_id,
            Worker.verification_status == "VERIFIED",
            Worker.availability_status != "OFFLINE",
            Worker.availability_status != "ON_LEAVE"
        )
        # Filter by primary skill or secondary skills contains service
        # For simplicity, get all and filter in Python for secondary skills check
        workers = query.all()
        eligible = []
        for w in workers:
            if w.primary_skill.lower() == job.service.lower():
                eligible.append(w)
            elif w.secondary_skills and any(job.service.lower() in s.lower() for s in w.secondary_skills):
                eligible.append(w)
        
        # If no primary match, return all verified workers as fallback (for demo)
        if not eligible and workers:
            # Return workers with same skill category loosely matched
            return workers[:20]
        
        return eligible
