"""
Anomaly Detection for Cooperative
Detects suspicious patterns: unusual job volume, earnings, reviews, cancellations
Uses Isolation Forest - lightweight, explainable
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from typing import List, Dict

class AnomalyDetector:
    def __init__(self, contamination=0.05):
        self.contamination = contamination
        self.model = IsolationForest(contamination=contamination, random_state=42)
    
    def detect_worker_anomalies(self, workers_df: pd.DataFrame, jobs_df: pd.DataFrame, payments_df: pd.DataFrame = None) -> List[Dict]:
        # Prepare features per worker
        worker_features = []
        
        job_counts = jobs_df.groupby('worker_id').size().to_dict()
        recent_jobs = jobs_df[jobs_df['status'] == 'COMPLETED']
        
        for _, worker in workers_df.iterrows():
            worker_id = worker['id']
            total_jobs = job_counts.get(worker_id, 0)
            this_week = worker['jobs_this_week']
            this_month = worker['jobs_this_month']
            rating = worker['rating']
            completion_rate = worker.get('completion_rate', 1.0)
            
            # Calculate earnings if payments available
            earnings = 0
            if payments_df is not None and not payments_df.empty:
                worker_jobs = recent_jobs[recent_jobs['worker_id'] == worker_id]
                if not worker_jobs.empty:
                    # Approximate earnings
                    earnings = worker_jobs['price'].sum() * 0.88
            
            worker_features.append({
                "worker_id": worker_id,
                "member_id": worker['member_id'],
                "primary_skill": worker['primary_skill'],
                "total_jobs": total_jobs,
                "jobs_this_week": this_week,
                "jobs_this_month": this_month,
                "rating": rating,
                "completion_rate": completion_rate,
                "experience": worker['experience_years'],
                "earnings_approx": earnings
            })
        
        features_df = pd.DataFrame(worker_features)
        
        if len(features_df) < 10:
            return []
        
        # Features for anomaly detection
        X = features_df[['total_jobs', 'jobs_this_week', 'jobs_this_month', 'rating', 'completion_rate']].fillna(0)
        
        # Fit model
        self.model.fit(X)
        scores = self.model.decision_function(X)
        predictions = self.model.predict(X)  # -1 = anomaly, 1 = normal
        
        anomalies = []
        for idx, (pred, score) in enumerate(zip(predictions, scores)):
            if pred == -1:
                worker = features_df.iloc[idx]
                reason, action = self.explain_anomaly(worker, features_df)
                anomalies.append({
                    "worker_id": int(worker['worker_id']),
                    "member_id": worker['member_id'],
                    "skill": worker['primary_skill'],
                    "anomaly_score": round(float(score), 3),
                    "pattern": reason,
                    "details": {
                        "jobs_this_week": int(worker['jobs_this_week']),
                        "jobs_this_month": int(worker['jobs_this_month']),
                        "total_jobs": int(worker['total_jobs']),
                        "rating": float(worker['rating']),
                        "completion_rate": float(worker['completion_rate'])
                    },
                    "severity": "HIGH" if score < -0.3 else "MEDIUM",
                    "action": action,
                    "flagged_at": pd.Timestamp.now().isoformat()
                })
        
        return anomalies
    
    def explain_anomaly(self, worker_row, all_workers_df):
        """Generate human-readable explanation"""
        avg_week = all_workers_df['jobs_this_week'].mean()
        avg_month = all_workers_df['jobs_this_month'].mean()
        
        reasons = []
        actions = []
        
        if worker_row['jobs_this_week'] > avg_week * 3:
            ratio = worker_row['jobs_this_week'] / avg_week if avg_week > 0 else 999
            reasons.append(f"Job volume {ratio:.1f}× normal daily average ({worker_row['jobs_this_week']} vs avg {avg_week:.1f})")
            actions.append("Review allocation algorithm - potential fairness issue")
        
        if worker_row['jobs_this_month'] > avg_month * 2.5:
            reasons.append(f"Monthly jobs {worker_row['jobs_this_month']} significantly above average {avg_month:.1f}")
            actions.append("Check if worker is overworked or system favoring")
        
        if worker_row['completion_rate'] < 0.7:
            reasons.append(f"Low completion rate {worker_row['completion_rate']:.0%} - possible quality or availability issue")
            actions.append("Investigate cancellations, offer support")
        
        if worker_row['rating'] < 3.0 and worker_row['total_jobs'] > 20:
            reasons.append(f"Low rating {worker_row['rating']} despite {worker_row['total_jobs']} jobs")
            actions.append("Quality review, training recommendation")
        
        if not reasons:
            reasons.append("Unusual pattern detected by model")
            actions.append("Manual review recommended")
        
        return " • ".join(reasons), " • ".join(actions)
    
    def detect_job_anomalies(self, jobs_df: pd.DataFrame) -> List[Dict]:
        """Detect suspicious job patterns"""
        anomalies = []
        
        # Check for repeated cancellations by same customer
        cancelled = jobs_df[jobs_df['status'] == 'CANCELLED']
        if not cancelled.empty:
            cancel_counts = cancelled.groupby('customer_id').size()
            frequent_cancellers = cancel_counts[cancel_counts > 5]
            for cust_id, count in frequent_cancellers.items():
                anomalies.append({
                    "type": "CUSTOMER",
                    "id": int(cust_id),
                    "pattern": f"Customer cancelled {count} jobs - possible abuse",
                    "severity": "MEDIUM",
                    "action": "Review customer history"
                })
        
        # Check for unusual pricing
        for service in jobs_df['service'].unique():
            service_jobs = jobs_df[jobs_df['service'] == service]
            if len(service_jobs) > 10:
                mean_price = service_jobs['price'].mean()
                std_price = service_jobs['price'].std()
                outliers = service_jobs[
                    (service_jobs['price'] > mean_price + 3*std_price) |
                    (service_jobs['price'] < mean_price - 3*std_price)
                ]
                for _, job in outliers.iterrows():
                    anomalies.append({
                        "type": "JOB",
                        "id": int(job['id']),
                        "pattern": f"Unusual price ₹{job['price']} for {service} (avg ₹{mean_price:.0f})",
                        "severity": "LOW",
                        "action": "Verify pricing"
                    })
        
        return anomalies[:10]  # Limit

def demo_anomalies():
    from .data_generator import SahakaarDataGenerator
    
    gen = SahakaarDataGenerator()
    dfs = gen.to_dataframes()
    
    # Inject an anomaly for demo
    # Make one worker have 3.7x normal jobs
    if len(dfs['workers']) > 10:
        dfs['workers'].loc[0, 'jobs_this_week'] = 15  # Normal is ~4
        dfs['workers'].loc[0, 'jobs_this_month'] = 80
    
    detector = AnomalyDetector(contamination=0.03)
    worker_anomalies = detector.detect_worker_anomalies(dfs['workers'], dfs['jobs'], dfs['payments'])
    job_anomalies = detector.detect_job_anomalies(dfs['jobs'])
    
    return {
        "worker_anomalies": worker_anomalies,
        "job_anomalies": job_anomalies,
        "total_flagged": len(worker_anomalies) + len(job_anomalies),
        "note": "System flags, NOT accuses. Review recommended. Demo uses synthetic data with injected anomaly for demonstration."
    }
