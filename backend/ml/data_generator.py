"""
Synthetic Data Generator for Sahakaar Seva
Generates realistic demo data for 500 workers, 100 customers, 10k jobs
Clearly labeled as synthetic for SIH demo
"""
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# For environments without faker, use simple lists
try:
    from faker import Faker
    fake = Faker('en_IN')
    HAS_FAKER = True
except ImportError:
    HAS_FAKER = False
    fake = None
    Faker = None

INDIAN_NAMES = [
    "Ramesh Kumar", "Sunil Yadav", "Amit Verma", "Priya Sharma", "Rohit Singh",
    "Sita Ram", "Mohan Lal", "Aslam Khan", "Rekha Devi", "Rajesh Kumar",
    "Anil Kumar", "Vikram Singh", "Sanjay Sharma", "Deepak Yadav", "Manish Kumar",
    "Pooja Kumari", "Kavita Singh", "Lakshmi Devi", "Gopal Das", "Harish Kumar",
    "Suresh Kumar", "Mahesh Singh", "Dinesh Kumar", "Ravi Kumar", "Ajay Singh",
    "Neha Sharma", "Sunita Devi", "Geeta Kumari", "Ritu Singh", "Kiran Devi"
]

FARIDABAD_LOCATIONS = [
    "Sector 15, Faridabad", "Sector 16, Faridabad", "Greenfields Colony",
    "Ballabgarh", "Old Faridabad", "NIT Faridabad", "Sector 21, Faridabad",
    "Surajkund", "Charmwood Village", "Sainik Colony", "Sarita Vihar",
    "Badarpur", "Tigaon", "Sector 37, Faridabad", "Sector 9, Faridabad"
]

SKILLS = ["electrician", "plumber", "carpenter", "cleaner"]
SECONDARY_SKILLS_MAP = {
    "electrician": ["wiring", "switchboard", "fan installation", "inverter", "EV charger", "lighting"],
    "plumber": ["pipe fitting", "leak repair", "bathroom fitting", "water heater", "drainage"],
    "carpenter": ["furniture repair", "door installation", "wardrobe", "modular kitchen", "polishing"],
    "cleaner": ["deep cleaning", "kitchen cleaning", "bathroom cleaning", "sofa cleaning", "house cleaning"]
}

class SahakaarDataGenerator:
    def __init__(self, seed=42):
        random.seed(seed)
        np.random.seed(seed)
        self.cooperative_id = 1
        
    def generate_cooperative(self):
        return {
            "id": 1,
            "name": "Faridabad Skilled Workers Cooperative",
            "registration_number": "FSWC/2024/HR/001",
            "description": "Labour Service Cooperative - 500 members providing electrical, plumbing, carpentry, cleaning services",
            "location": "Faridabad, Haryana",
            "latitude": 28.4089,
            "longitude": 77.3178,
            "total_members": 500
        }
    
    def generate_users_and_workers(self, num_workers=500, num_customers=100):
        workers = []
        users = []
        
        # Skill distribution as per spec: 120 elec, 95 plum, 80 carp, 205 clean = 500
        skill_counts = {"electrician": 120, "plumber": 95, "carpenter": 80, "cleaner": 205}
        
        user_id = 1
        
        # Generate worker users
        worker_idx = 0
        for skill, count in skill_counts.items():
            for i in range(count):
                name = random.choice(INDIAN_NAMES) + f" {random.randint(1,99)}"
                phone = f"9{random.randint(100000000, 999999999)}"
                
                user = {
                    "id": user_id,
                    "name": name,
                    "phone": phone,
                    "email": f"worker{user_id}@demo.sahakaar.local",
                    "password_hash": "$2b$12$demo_hash_for_sih_prototype",  # will be hashed properly in seed script
                    "role": "WORKER",
                    "is_active": True,
                    "location_text": random.choice(FARIDABAD_LOCATIONS)
                }
                users.append(user)
                
                # Worker details
                exp = random.choices([1,2,3,5,8,10,12,15,20], weights=[5,10,15,20,15,15,10,7,3])[0]
                rating = round(random.uniform(3.5, 5.0), 1)
                total_jobs = random.randint(10, 800)
                
                # Secondary skills
                sec_skills = random.sample(SECONDARY_SKILLS_MAP[skill], k=random.randint(1,3))
                
                # Availability - 80% available
                avail = random.choices(
                    ["AVAILABLE", "BUSY", "OFFLINE", "ON_LEAVE"],
                    weights=[80, 10, 7, 3]
                )[0]
                
                verification = random.choices(
                    ["VERIFIED", "PENDING", "UNDER_REVIEW"],
                    weights=[97, 2, 1]
                )[0]
                
                # Location jitter around Faridabad
                lat = 28.4089 + random.uniform(-0.1, 0.1)
                lon = 77.3178 + random.uniform(-0.1, 0.1)
                
                member_id = f"FSWC-{skill[0].upper()}-{100+worker_idx}"
                
                worker = {
                    "id": worker_idx + 1,
                    "user_id": user_id,
                    "cooperative_id": 1,
                    "member_id": member_id,
                    "primary_skill": skill,
                    "secondary_skills": sec_skills,
                    "experience_years": exp,
                    "rating": rating,
                    "total_jobs": total_jobs,
                    "completed_jobs": int(total_jobs * random.uniform(0.85, 0.98)),
                    "jobs_this_week": random.randint(0, 8),
                    "jobs_this_month": random.randint(5, 40),
                    "availability_status": avail,
                    "verification_status": verification,
                    "latitude": lat,
                    "longitude": lon,
                    "completion_rate": round(random.uniform(0.85, 1.0), 2),
                    "avg_response_time_minutes": random.randint(10, 90),
                    "insurance_status": random.choices(["ACTIVE", "PENDING"], weights=[85,15])[0]
                }
                workers.append(worker)
                user_id += 1
                worker_idx += 1
        
        # Generate customer users
        for i in range(num_customers):
            name = f"Customer {i+1} " + random.choice(INDIAN_NAMES).split()[-1]
            phone = f"8{random.randint(100000000, 999999999)}"
            user = {
                "id": user_id,
                "name": name,
                "phone": phone,
                "email": f"customer{user_id}@demo.sahakaar.local",
                "password_hash": "$2b$12$demo_hash_for_sih_prototype",
                "role": "CUSTOMER",
                "is_active": True,
                "location_text": random.choice(FARIDABAD_LOCATIONS)
            }
            users.append(user)
            user_id += 1
        
        # Add cooperative admin
        admin_user = {
            "id": user_id,
            "name": "Cooperative Admin",
            "phone": "9999999999",
            "email": "admin@fswc.coop",
            "password_hash": "$2b$12$demo_hash_for_sih_prototype",
            "role": "COOPERATIVE_ADMIN",
            "is_active": True,
            "location_text": "Faridabad"
        }
        users.append(admin_user)
        
        return users, workers
    
    def generate_jobs(self, num_jobs=10000, customers=None, workers=None):
        jobs = []
        start_date = datetime.now() - timedelta(days=365)
        
        services = ["electrician", "plumber", "carpenter", "cleaner"]
        sub_services_map = SECONDARY_SKILLS_MAP
        
        # Seasonal demand pattern: electrical high in summer, cleaning high before festivals
        for i in range(num_jobs):
            # Random date in last 12 months
            days_ago = random.randint(0, 365)
            created_at = datetime.now() - timedelta(days=days_ago)
            
            # Service with seasonal bias
            month = created_at.month
            if month in [4,5,6]:  # summer - electrical high
                service = random.choices(services, weights=[40,20,15,25])[0]
            elif month in [10,11]:  # Diwali cleaning season
                service = random.choices(services, weights=[20,15,15,50])[0]
            else:
                service = random.choices(services, weights=[30,25,20,25])[0]
            
            sub_service = random.choice(sub_services_map[service])
            
            # Customer
            customer_id = random.randint(501, 600) if customers else random.randint(1,100)
            
            # Worker (if completed)
            worker_id = None
            status = random.choices(
                ["COMPLETED", "COMPLETED", "COMPLETED", "COMPLETED", "CANCELLED", "IN_PROGRESS"],
                weights=[80,10,5,2,2,1]
            )[0]
            
            if status in ["COMPLETED", "IN_PROGRESS"] and workers:
                # Find worker with matching skill
                matching = [w for w in workers if w["primary_skill"] == service]
                if matching:
                    worker_id = random.choice(matching)["id"]
            
            price_map = {"electrician": [300,800], "plumber": [250,700], "carpenter": [400,1200], "cleaner": [500,1500]}
            price = random.randint(price_map[service][0], price_map[service][1])
            
            job = {
                "id": i+1,
                "customer_id": customer_id,
                "cooperative_id": 1,
                "worker_id": worker_id,
                "service": service,
                "sub_service": sub_service,
                "description": f"{sub_service} required at {random.choice(FARIDABAD_LOCATIONS)}",
                "location": random.choice(FARIDABAD_LOCATIONS),
                "latitude": 28.4089 + random.uniform(-0.1,0.1),
                "longitude": 77.3178 + random.uniform(-0.1,0.1),
                "price": price,
                "status": status,
                "priority": random.choices(["LOW","NORMAL","HIGH","URGENT"], weights=[10,70,15,5])[0],
                "created_at": created_at,
                "completed_at": created_at + timedelta(hours=random.randint(1,48)) if status=="COMPLETED" else None
            }
            jobs.append(job)
        
        return jobs
    
    def generate_payments(self, jobs):
        payments = []
        for job in jobs:
            if job["status"] != "COMPLETED":
                continue
            total = job["price"]
            worker_pct = 88.0
            coop_pct = 6.0
            plat_pct = 6.0
            
            payments.append({
                "job_id": job["id"],
                "total_amount": total,
                "worker_amount": round(total*worker_pct/100,2),
                "cooperative_amount": round(total*coop_pct/100,2),
                "platform_amount": round(total*plat_pct/100,2),
                "worker_percentage": worker_pct,
                "cooperative_percentage": coop_pct,
                "platform_percentage": plat_pct,
                "payment_status": "COMPLETED",
                "transaction_id": f"TXN-DEMO-{job['id']:06d}"
            })
        return payments
    
    def to_dataframes(self):
        coop = self.generate_cooperative()
        users, workers = self.generate_users_and_workers()
        jobs = self.generate_jobs(customers=users, workers=workers)
        payments = self.generate_payments(jobs)
        
        return {
            "cooperative": pd.DataFrame([coop]),
            "users": pd.DataFrame(users),
            "workers": pd.DataFrame(workers),
            "jobs": pd.DataFrame(jobs),
            "payments": pd.DataFrame(payments)
        }

if __name__ == "__main__":
    gen = SahakaarDataGenerator()
    dfs = gen.to_dataframes()
    for name, df in dfs.items():
        print(f"\n=== {name.upper()} ===")
        print(f"Shape: {df.shape}")
        print(df.head(2))
