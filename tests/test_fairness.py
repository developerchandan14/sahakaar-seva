import sys
sys.path.append('..')
from backend.services.job_assignment import FairJobAssignmentEngine
from backend.models.worker import Worker
from backend.models.job import Job

# Mock worker class for testing
class MockWorker:
    def __init__(self, id, skill, jobs_week, jobs_total, rating, avail="AVAILABLE", exp=5, comp_rate=1.0, lat=28.4, lon=77.3):
        self.id = id
        self.member_id = f"FSWC-E-{id}"
        self.primary_skill = skill
        self.secondary_skills = []
        self.jobs_this_week = jobs_week
        self.total_jobs = jobs_total
        self.rating = rating
        self.availability_status = avail
        self.experience_years = exp
        self.completion_rate = comp_rate
        self.avg_response_time_minutes = 20
        self.latitude = lat
        self.longitude = lon

class MockJob:
    def __init__(self, service="electrician", lat=28.4, lon=77.3):
        self.service = service
        self.sub_service = "switchboard"
        self.latitude = lat
        self.longitude = lon

def test_fairness_boost():
    """Worker with 0 jobs should be boosted over worker with 8 jobs when skill equal"""
    engine = FairJobAssignmentEngine()
    job = MockJob()
    
    worker_a = MockWorker(1, "electrician", 8, 100, 5.0)
    worker_b = MockWorker(2, "electrician", 2, 50, 4.8)
    worker_c = MockWorker(3, "electrician", 0, 10, 4.7)
    
    all_workers = [worker_a, worker_b, worker_c]
    
    score_a = engine.score_worker(worker_a, job, all_workers)
    score_b = engine.score_worker(worker_b, job, all_workers)
    score_c = engine.score_worker(worker_c, job, all_workers)
    
    print(f"Worker A (8 jobs, 5.0 rating): {score_a['final_score']} - workload {score_a['breakdown']['workload_balance']}, fairness {score_a['breakdown']['fairness']}")
    print(f"Worker B (2 jobs, 4.8 rating): {score_b['final_score']} - workload {score_b['breakdown']['workload_balance']}, fairness {score_b['breakdown']['fairness']}")
    print(f"Worker C (0 jobs, 4.7 rating): {score_c['final_score']} - workload {score_c['breakdown']['workload_balance']}, fairness {score_c['breakdown']['fairness']}")
    
    # C should have highest fairness and workload scores
    assert score_c['breakdown']['workload_balance'] > score_a['breakdown']['workload_balance'], "Fairness: 0-job worker should have higher workload score"
    assert score_c['breakdown']['fairness'] > score_a['breakdown']['fairness'], "Fairness: 0-job worker should have higher fairness score"
    
    print("✓ Fairness boost test passed: System prevents top-rated monopoly")

def test_skill_match():
    engine = FairJobAssignmentEngine()
    job = MockJob(service="electrician")
    
    worker_match = MockWorker(1, "electrician", 2, 50, 4.5)
    worker_no_match = MockWorker(2, "plumber", 0, 10, 5.0)
    
    score_match = engine.calculate_skill_match(worker_match, job)
    score_no_match = engine.calculate_skill_match(worker_no_match, job)
    
    print(f"Skill match (electrician for electrician job): {score_match}")
    print(f"Skill no match (plumber for electrician job): {score_no_match}")
    
    assert score_match > score_no_match, "Skill match should be higher for matching skill"
    print("✓ Skill match test passed")

def test_payment_validation():
    from backend.services.payment_service import PaymentService
    
    assert PaymentService.validate_percentages(88, 6, 6) == True
    assert PaymentService.validate_percentages(80, 10, 10) == True
    assert PaymentService.validate_percentages(50, 25, 25) == True
    assert PaymentService.validate_percentages(40, 30, 30) == False  # worker <50
    assert PaymentService.validate_percentages(88, 6, 5) == False  # sum 99
    assert PaymentService.validate_percentages(90, 5, 5) == True
    
    print("✓ Payment validation test passed")

def test_payment_split():
    from backend.services.payment_service import PaymentService
    
    split = PaymentService.calculate_split(500, 88, 6, 6)
    assert split['total_amount'] == 500
    assert abs(split['worker_amount'] + split['cooperative_amount'] + split['platform_amount'] - 500) < 0.01
    assert split['worker_amount'] == 440
    
    print(f"Payment split ₹500: Worker ₹{split['worker_amount']}, Coop ₹{split['cooperative_amount']}, Platform ₹{split['platform_amount']}")
    print("✓ Payment split test passed")

if __name__ == "__main__":
    test_fairness_boost()
    test_skill_match()
    test_payment_validation()
    test_payment_split()
    print("\nAll tests passed! ✓")
