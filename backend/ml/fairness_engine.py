"""
Opportunity Equity Index
Calculates fairness of job distribution across workers and skills
"""
import pandas as pd
import numpy as np
from typing import Dict, List

class FairnessEngine:
    def __init__(self):
        pass
    
    def calculate_gini(self, values: List[float]) -> float:
        """Gini coefficient - 0 = perfect equality, 1 = max inequality"""
        if len(values) == 0:
            return 0
        values = np.array(values)
        if np.all(values == 0):
            return 0
        sorted_vals = np.sort(values)
        n = len(values)
        cumsum = np.cumsum(sorted_vals)
        return (n + 1 - 2 * np.sum(cumsum) / cumsum[-1]) / n if cumsum[-1] != 0 else 0
    
    def calculate_opportunity_equity(self, workers_df: pd.DataFrame, jobs_df: pd.DataFrame) -> Dict:
        """
        Calculate Opportunity Equity Index 0-100
        100 = perfect fair distribution
        """
        # Jobs per worker in last 30 days
        recent_jobs = jobs_df[jobs_df['status'] == 'COMPLETED'].copy()
        
        # Count jobs per worker
        worker_job_counts = recent_jobs['worker_id'].value_counts().to_dict()
        
        # Map to all workers (including 0 jobs)
        all_counts = []
        skill_groups = {}
        
        for _, worker in workers_df.iterrows():
            count = worker_job_counts.get(worker['id'], 0)
            all_counts.append(count)
            
            skill = worker['primary_skill']
            if skill not in skill_groups:
                skill_groups[skill] = []
            skill_groups[skill].append(count)
        
        # Overall Gini
        gini = self.calculate_gini(all_counts)
        equity_score = int((1 - gini) * 100)
        
        # Per-skill analysis
        skill_equity = {}
        avg_jobs_by_skill = {}
        overall_avg = np.mean(all_counts) if all_counts else 0
        
        for skill, counts in skill_groups.items():
            skill_gini = self.calculate_gini(counts)
            skill_equity[skill] = int((1 - skill_gini) * 100)
            avg_jobs_by_skill[skill] = round(float(np.mean(counts)), 2) if counts else 0
        
        # Identify under-allocated
        under_allocated = []
        for skill, avg in avg_jobs_by_skill.items():
            if overall_avg > 0 and avg < overall_avg * 0.6:
                diff_pct = ((overall_avg - avg) / overall_avg * 100)
                under_allocated.append({
                    "skill": skill,
                    "avg_jobs": avg,
                    "cooperative_avg": round(overall_avg, 2),
                    "diff_percent": round(diff_pct, 1),
                    "status": "⚠ Under-allocated"
                })
        
        return {
            "opportunity_equity_index": equity_score,
            "gini_coefficient": round(gini, 3),
            "overall_avg_jobs": round(float(overall_avg), 2),
            "skill_equity": skill_equity,
            "avg_jobs_by_skill": avg_jobs_by_skill,
            "under_allocated_skills": under_allocated,
            "total_workers": len(workers_df),
            "total_jobs_analyzed": len(recent_jobs),
            "explanation": self.generate_explanation(equity_score, under_allocated, avg_jobs_by_skill, overall_avg)
        }
    
    def generate_explanation(self, equity_score, under_allocated, avg_by_skill, overall_avg):
        explanations = []
        
        if equity_score >= 85:
            explanations.append(f"Good equity: {equity_score}/100. Jobs fairly distributed.")
        elif equity_score >= 70:
            explanations.append(f"Moderate equity: {equity_score}/100. Some imbalance exists.")
        else:
            explanations.append(f"Low equity: {equity_score}/100. Significant imbalance - cooperative intervention needed.")
        
        for ua in under_allocated:
            explanations.append(
                f"{ua['skill'].capitalize()}s receiving {ua['diff_percent']}% fewer jobs than cooperative average "
                f"({ua['avg_jobs']} vs {ua['cooperative_avg']}). Possible reasons: low demand, low visibility, availability, service mismatch."
            )
        
        return explanations
    
    def get_recommendations(self, equity_data: Dict) -> List[str]:
        recs = []
        for ua in equity_data['under_allocated_skills']:
            skill = ua['skill']
            recs.append(f"Promote {skill} services to customers")
            recs.append(f"Investigate {skill} worker availability")
            recs.append(f"Check if {skill} service categories need expansion")
        
        if equity_data['opportunity_equity_index'] < 75:
            recs.append("Enable fairness boost in AI job allocation")
            recs.append("Review workers with 0 jobs in last 7 days")
        
        return recs

def demo_fairness():
    from .data_generator import SahakaarDataGenerator
    gen = SahakaarDataGenerator()
    dfs = gen.to_dataframes()
    
    engine = FairnessEngine()
    result = engine.calculate_opportunity_equity(dfs['workers'], dfs['jobs'])
    result['recommendations'] = engine.get_recommendations(result)
    result['note'] = "Demo uses synthetic data"
    return result
