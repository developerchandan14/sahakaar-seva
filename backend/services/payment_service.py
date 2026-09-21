from sqlalchemy.orm import Session
from ..models.policy import CooperativePolicy
from ..models.payment import Payment, PaymentStatus
from ..models.job import Job
from ..config import settings
import uuid

class PaymentService:
    @staticmethod
    def get_active_policy(db: Session, cooperative_id: int) -> CooperativePolicy:
        policy = db.query(CooperativePolicy).filter(
            CooperativePolicy.cooperative_id == cooperative_id,
            CooperativePolicy.is_active == "true"
        ).order_by(CooperativePolicy.effective_from.desc()).first()
        
        if not policy:
            # Create default policy if none exists
            policy = CooperativePolicy(
                cooperative_id=cooperative_id,
                worker_percentage=settings.DEFAULT_WORKER_PERCENTAGE,
                cooperative_percentage=settings.DEFAULT_COOPERATIVE_PERCENTAGE,
                platform_percentage=settings.DEFAULT_PLATFORM_PERCENTAGE,
                notes="Default policy - auto created"
            )
            db.add(policy)
            db.commit()
            db.refresh(policy)
        return policy
    
    @staticmethod
    def validate_percentages(worker: float, cooperative: float, platform: float) -> bool:
        total = worker + cooperative + platform
        return abs(total - 100.0) < 0.01 and worker >= 50 and cooperative >= 0 and platform >= 0
    
    @staticmethod
    def calculate_split(total_amount: float, worker_pct: float, coop_pct: float, platform_pct: float) -> dict:
        if not PaymentService.validate_percentages(worker_pct, coop_pct, platform_pct):
            raise ValueError(f"Invalid percentages: {worker_pct}+{coop_pct}+{platform_pct} must equal 100")
        
        worker_amount = round(total_amount * worker_pct / 100, 2)
        coop_amount = round(total_amount * coop_pct / 100, 2)
        platform_amount = round(total_amount * platform_pct / 100, 2)
        
        # Adjust for rounding
        diff = total_amount - (worker_amount + coop_amount + platform_amount)
        worker_amount += round(diff, 2)
        
        return {
            "total_amount": total_amount,
            "worker_amount": worker_amount,
            "cooperative_amount": coop_amount,
            "platform_amount": platform_amount,
            "worker_percentage": worker_pct,
            "cooperative_percentage": coop_pct,
            "platform_percentage": platform_pct
        }
    
    @staticmethod
    def create_payment_for_job(db: Session, job: Job) -> Payment:
        policy = PaymentService.get_active_policy(db, job.cooperative_id)
        split = PaymentService.calculate_split(
            job.price,
            policy.worker_percentage,
            policy.cooperative_percentage,
            policy.platform_percentage
        )
        
        payment = Payment(
            job_id=job.id,
            total_amount=split["total_amount"],
            worker_amount=split["worker_amount"],
            cooperative_amount=split["cooperative_amount"],
            platform_amount=split["platform_amount"],
            worker_percentage=split["worker_percentage"],
            cooperative_percentage=split["cooperative_percentage"],
            platform_percentage=split["platform_percentage"],
            payment_status=PaymentStatus.PENDING,
            transaction_id=f"TXN-{uuid.uuid4().hex[:12].upper()}",
            payment_method="UPI_MOCK_DEMO"
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment
    
    @staticmethod
    def get_transparency_message(payment: Payment) -> dict:
        return {
            "customer_paid": payment.total_amount,
            "worker_received": payment.worker_amount,
            "worker_percentage": payment.worker_percentage,
            "cooperative_received": payment.cooperative_amount,
            "platform_costs": payment.platform_amount,
            "message_customer": f"Customer paid ₹{payment.total_amount}. Transparent settlement.",
            "message_worker": f"Customer paid ₹{payment.total_amount}. You received ₹{payment.worker_amount} ({payment.worker_percentage}%). Cooperative fee ₹{payment.cooperative_amount} used for insurance + training + operations.",
            "breakdown": {
                "worker": f"₹{payment.worker_amount} ({payment.worker_percentage}%)",
                "cooperative": f"₹{payment.cooperative_amount} ({payment.cooperative_percentage}%) - Admin, Training, Verification, Welfare",
                "platform": f"₹{payment.platform_amount} ({payment.platform_percentage}%) - Digital ops, gateway"
            }
        }
