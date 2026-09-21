"""
Training Recommendation Engine
Identifies skill gaps based on demand forecast and worker skills
"""
import pandas as pd
import numpy as np
from typing import List, Dict
from datetime import datetime

class TrainingRecommender:
    def __init__(self):
        self.emerging_skills = {
            "electrician": ["EV charger installation", "Solar panel installation", "Smart home wiring", "Inverter & battery"],
            "plumber": ["Water heater", "RO installation", "Smart bathroom", "Rainwater harvesting"],
            "carpenter": ["Modular kitchen", "Wardrobe design", "UPVC", "Polishing & lamination"],
            "cleaner": ["Deep cleaning", "Sanitization", "Sofa & carpet", "Kitchen deep clean"]
        }
    
    def analyze_skill_gaps(self, workers_df: pd.DataFrame, jobs_df: pd.DataFrame, forecasts: List[Dict]) -> List[Dict]:
        gaps = []
        
        # Current trained count per skill
        for service in workers_df['primary_skill'].unique():
            # Workers with this primary skill
            skilled_workers = workers_df[workers_df['primary_skill'] == service]
            
            # Check secondary skills
            secondary_counts = {}
            for _, w in skilled_workers.iterrows():
                for sec in w['secondary_skills']:
                    secondary_counts[sec] = secondary_counts.get(sec, 0) + 1
            
            # Find forecast for this service
            forecast = next((f for f in forecasts if f['service'] == service), None)
            if not forecast:
                continue
            
            # Demand analysis
            current_avg = forecast['current_avg']
            forecast_avg = forecast['forecast_avg']
            change_pct = forecast['change_percent']
            
            if change_pct > 15:
                # Need more workers
                # Estimate required workers: forecast demand / avg jobs per worker
                avg_jobs_per_worker = skilled_workers['jobs_this_month'].mean() if len(skilled_workers) > 0 else 10
                if avg_jobs_per_worker == 0:
                    avg_jobs_per_worker = 10
                
                # Rough estimate: need workers = forecast daily * 30 / avg monthly jobs
                estimated_monthly_demand = forecast_avg * 30
                current_capacity = len(skilled_workers) * avg_jobs_per_worker
                required_workers = int(estimated_monthly_demand / avg_jobs_per_worker) if avg_jobs_per_worker > 0 else len(skilled_workers)
                shortage = max(0, required_workers - len(skilled_workers))
                
                if shortage > 0 or change_pct > 25:
                    gaps.append({
                        "skill": service,
                        "sub_skill": self.emerging_skills.get(service, ["General"])[0],
                        "current_trained": len(skilled_workers),
                        "required": required_workers,
                        "shortage": shortage,
                        "demand_increase_percent": change_pct,
                        "current_avg_daily": current_avg,
                        "forecast_avg_daily": forecast_avg,
                        "secondary_skill_coverage": secondary_counts,
                        "recommended_action": f"TRAIN {max(3, shortage)}-{max(5, shortage+3)} {service.upper()}S IN {self.emerging_skills.get(service, ['Advanced'])[0].upper()}",
                        "reason": f"{service.capitalize()} demand ↑ {change_pct:.0f}%. Current {len(skilled_workers)} trained, forecast requires {required_workers}. Shortage: {shortage}",
                        "priority": "HIGH" if change_pct > 30 else "MEDIUM"
                    })
            
            # Check for low-rated jobs indicating training need
            low_rated_jobs = jobs_df[
                (jobs_df['service'] == service) & 
                (jobs_df['worker_id'].isin(skilled_workers['id'].tolist()))
            ]
            # In real system, join with reviews
            # For demo, check if workers have low completion rate
            low_performers = skilled_workers[skilled_workers['rating'] < 4.0]
            if len(low_performers) > len(skilled_workers) * 0.15:
                gaps.append({
                    "skill": service,
                    "sub_skill": "Quality improvement",
                    "current_trained": len(skilled_workers),
                    "required": len(low_performers),
                    "shortage": 0,
                    "demand_increase_percent": 0,
                    "reason": f"{len(low_performers)} {service}s have rating <4.0. Quality training needed.",
                    "recommended_action": f"Quality training for {len(low_performers)} {service}s",
                    "priority": "MEDIUM"
                })
        
        return gaps
    
    def recommend_workers_for_training(self, workers_df: pd.DataFrame, gap: Dict) -> List[Dict]:
        """Which specific workers should get training"""
        service = gap['skill']
        candidates = workers_df[workers_df['primary_skill'] == service].copy()
        
        # Score workers for training suitability
        # Prefer: low secondary skill coverage, medium experience, high availability, lower recent jobs (can spare time)
        recommendations = []
        for _, w in candidates.iterrows():
            # If worker doesn't have the emerging skill, prioritize
            has_emerging = any(gap['sub_skill'].lower() in s.lower() for s in w['secondary_skills'])
            
            score = 0
            if not has_emerging:
                score += 40
            if w['experience_years'] >= 3 and w['experience_years'] <= 10:
                score += 20  # Mid-level most trainable
            if w['jobs_this_week'] <= 3:
                score += 20  # Has time
            if w['rating'] >= 4.0:
                score += 20  # Good performer
            
            recommendations.append({
                "worker_id": w['id'],
                "member_id": w['member_id'],
                "name": f"Worker {w['id']}",
                "experience": w['experience_years'],
                "rating": w['rating'],
                "has_skill": has_emerging,
                "training_score": score
            })
        
        recommendations.sort(key=lambda x: x['training_score'], reverse=True)
        return recommendations[:gap['shortage']+5] if gap['shortage'] > 0 else recommendations[:5]

def demo_training_recommendations():
    from .data_generator import SahakaarDataGenerator
    from .demand_forecasting import DemandForecaster
    
    gen = SahakaarDataGenerator()
    dfs = gen.to_dataframes()
    
    forecaster = DemandForecaster()
    forecasts = forecaster.forecast_all(dfs['jobs'])
    
    recommender = TrainingRecommender()
    gaps = recommender.analyze_skill_gaps(dfs['workers'], dfs['jobs'], forecasts)
    
    # Add worker recommendations for top gap
    for gap in gaps[:2]:
        gap['recommended_workers'] = recommender.recommend_workers_for_training(dfs['workers'], gap)
    
    return {
        "gaps": gaps,
        "total_gaps": len(gaps),
        "note": "Demo uses synthetic data. Production will use real demand + skill data."
    }
