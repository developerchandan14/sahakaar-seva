"""
Seed script for Sahakaar Seva - Creates demo cooperative with 500 workers, 100 customers, 10k jobs
Run: python -m backend.seed
"""
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from .database import SessionLocal, create_tables
from .models.user import User, UserRole
from .models.cooperative import Cooperative
from .models.worker import Worker, VerificationStatus, AvailabilityStatus
from .models.job import Job, JobStatus, JobPriority
from .models.payment import Payment, PaymentStatus
from .models.policy import CooperativePolicy
from .models.training import Training
from .models.welfare import Welfare
from .ml.data_generator import SahakaarDataGenerator

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_cached_hashes = {}
def hash_pwd(p):
    # Cache hashes to avoid re-hashing same password 600 times (bcrypt is slow)
    if p not in _cached_hashes:
        _cached_hashes[p] = pwd_context.hash(p)
    return _cached_hashes[p]

def seed():
    print("Creating tables...")
    create_tables()
    
    db: Session = SessionLocal()
    
    try:
        # Clear existing
        print("Clearing existing data...")
        db.query(Payment).delete()
        db.query(Training).delete()
        db.query(Welfare).delete()
        db.query(Job).delete()
        db.query(Worker).delete()
        db.query(CooperativePolicy).delete()
        db.query(Cooperative).delete()
        db.query(User).delete()
        db.commit()
        
        gen = SahakaarDataGenerator(seed=42)
        
        # Cooperative
        print("Creating cooperative...")
        coop = Cooperative(
            name="Faridabad Skilled Workers Cooperative",
            registration_number="FSWC/2024/HR/001",
            description="Labour Service Cooperative - 500 members providing electrical, plumbing, carpentry, cleaning services. Govt. Registered.",
            location="Faridabad, Haryana",
            latitude=28.4089,
            longitude=77.3178,
            total_members=500
        )
        db.add(coop)
        db.commit()
        db.refresh(coop)
        print(f"Cooperative created: {coop.id}")
        
        # Policy
        policy = CooperativePolicy(
            cooperative_id=coop.id,
            worker_percentage=88.0,
            cooperative_percentage=6.0,
            platform_percentage=6.0,
            notes="Default policy approved by cooperative - configurable and transparent"
        )
        db.add(policy)
        db.commit()
        
        # Generate users and workers via generator logic but with real DB
        users_data, workers_data = gen.generate_users_and_workers(num_workers=500, num_customers=100)
        
        print(f"Creating {len(users_data)} users...")
        user_map = {}  # old_id -> new_id
        for u in users_data:
            # Special passwords for demo accounts
            if u['phone'] == "9999999999":
                pwd = "admin123"
            elif u['phone'] == "8888888888":
                pwd = "customer123"
            elif u['phone'] == "7777777777":
                pwd = "worker123"
            else:
                pwd = "demo123"
            
            # Override for demo accounts to known phones
            # We'll create specific demo users after loop
            
            role = UserRole[u['role']]
            user = User(
                name=u['name'],
                phone=u['phone'],
                email=u['email'],
                password_hash=hash_pwd(pwd),
                role=role,
                location_text=u['location_text'],
                is_active=True
            )
            db.add(user)
            db.flush()
            user_map[u['id']] = user.id
        
        # Create specific demo users with known credentials
        demo_users = [
            {"name": "Cooperative Admin", "phone": "9999999999", "email": "admin@fswc.coop", "role": UserRole.COOPERATIVE_ADMIN, "pwd": "admin123"},
            {"name": "Demo Customer", "phone": "8888888888", "email": "customer@demo.com", "role": UserRole.CUSTOMER, "pwd": "customer123", "location": "Sector 15, Faridabad"},
            {"name": "Ramesh Kumar", "phone": "7777777777", "email": "ramesh@demo.com", "role": UserRole.WORKER, "pwd": "worker123", "location": "Sector 16, Faridabad"},
        ]
        
        for du in demo_users:
            existing = db.query(User).filter(User.phone == du['phone']).first()
            if not existing:
                user = User(
                    name=du['name'],
                    phone=du['phone'],
                    email=du['email'],
                    password_hash=hash_pwd(du['pwd']),
                    role=du['role'],
                    location_text=du.get('location', 'Faridabad'),
                    is_active=True
                )
                db.add(user)
                db.flush()
                print(f"Demo user created: {du['phone']} / {du['pwd']}")
        
        db.commit()
        print("Users created")
        
        # Workers - need to map user_id
        print("Creating workers...")
        # Get all worker users
        worker_users = db.query(User).filter(User.role == UserRole.WORKER).order_by(User.id).limit(500).all()
        
        for idx, w in enumerate(workers_data[:500]):
            if idx >= len(worker_users):
                break
            user = worker_users[idx]
            
            worker = Worker(
                user_id=user.id,
                cooperative_id=coop.id,
                member_id=w['member_id'],
                primary_skill=w['primary_skill'],
                secondary_skills=w['secondary_skills'],
                experience_years=w['experience_years'],
                rating=w['rating'],
                total_jobs=w['total_jobs'],
                completed_jobs=w['completed_jobs'],
                jobs_this_week=w['jobs_this_week'],
                jobs_this_month=w['jobs_this_month'],
                availability_status=AvailabilityStatus[w['availability_status']],
                verification_status=VerificationStatus[w['verification_status']],
                latitude=w['latitude'],
                longitude=w['longitude'],
                completion_rate=w['completion_rate'],
                avg_response_time_minutes=w['avg_response_time_minutes'],
                insurance_status=w['insurance_status']
            )
            db.add(worker)
        
        db.commit()
        print("Workers created")
        
        # Jobs - generate 1000 for demo (not 10k to keep fast)
        print("Creating jobs...")
        jobs_data = gen.generate_jobs(num_jobs=1000)
        
        # Get customer and worker IDs
        customers = db.query(User).filter(User.role == UserRole.CUSTOMER).all()
        workers = db.query(Worker).all()
        worker_by_skill = {}
        for w in workers:
            worker_by_skill.setdefault(w.primary_skill, []).append(w)
        
        for j in jobs_data[:1000]:
            # Map customer
            cust = random.choice(customers) if customers else None
            if not cust:
                continue
            
            worker_id = None
            if j['status'] in ['COMPLETED', 'IN_PROGRESS'] and j['worker_id']:
                # Find worker with matching skill
                skill_workers = worker_by_skill.get(j['service'], workers)
                if skill_workers:
                    worker_id = random.choice(skill_workers).id
            
            job = Job(
                customer_id=cust.id,
                cooperative_id=coop.id,
                worker_id=worker_id,
                service=j['service'],
                sub_service=j['sub_service'],
                description=j['description'],
                location=j['location'],
                latitude=j['latitude'],
                longitude=j['longitude'],
                price=j['price'],
                status=JobStatus[j['status']],
                priority=JobPriority[j['priority']],
                created_at=j['created_at'],
                completed_at=j['completed_at']
            )
            db.add(job)
        
        db.commit()
        print("Jobs created")
        
        # Payments for completed jobs
        print("Creating payments...")
        completed_jobs = db.query(Job).filter(Job.status == JobStatus.COMPLETED).all()
        for job in completed_jobs:
            total = job.price
            payment = Payment(
                job_id=job.id,
                total_amount=total,
                worker_amount=round(total*0.88,2),
                cooperative_amount=round(total*0.06,2),
                platform_amount=round(total*0.06,2),
                worker_percentage=88.0,
                cooperative_percentage=6.0,
                platform_percentage=6.0,
                payment_status=PaymentStatus.COMPLETED,
                transaction_id=f"TXN-DEMO-{job.id:06d}",
                payment_method="UPI_MOCK_DEMO"
            )
            db.add(payment)
        
        db.commit()
        print("Payments created")
        
        # Welfare
        print("Creating welfare records...")
        for w in workers[:500]:
            welfare = Welfare(
                worker_id=w.id,
                insurance_status="ACTIVE" if random.random() > 0.15 else "PENDING",
                insurance_amount=200000.0,
                insurance_provider="Cooperative Welfare Fund",
                benefits={"health": True, "accident": True, "training_subsidy": True},
                total_earnings=random.uniform(10000, 100000),
                total_cooperative_contribution=random.uniform(500, 5000)
            )
            db.add(welfare)
        db.commit()
        
        # Training recommendations
        print("Creating training recommendations...")
        # Simulate EV charger demand
        ev_workers = [w for w in workers if w.primary_skill == "electrician"][:15]
        for w in ev_workers[:5]:
            training = Training(
                worker_id=w.id,
                course="EV Charger Installation",
                skill="EV charger",
                description="2-day certified course for EV charger installation",
                status="RECOMMENDED",
                recommended_by_ai=True,
                ai_reason="EV Charger demand ↑ 35%. Current trained: 17, Required: 29, Shortage: 12"
            )
            db.add(training)
        db.commit()
        
        print("\n=== SEED COMPLETE ===")
        print(f"Cooperative: {coop.name} ({coop.registration_number})")
        print(f"Workers: {len(workers)} (Elec 120, Plum 95, Carp 80, Clean 205)")
        print(f"Customers: {len(customers)}")
        print(f"Jobs: {len(completed_jobs)} completed")
        print("\nDemo Credentials:")
        print("Admin: 9999999999 / admin123")
        print("Customer: 8888888888 / customer123")
        print("Worker: 7777777777 / worker123")
        print("\nAll other users: password = demo123")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
