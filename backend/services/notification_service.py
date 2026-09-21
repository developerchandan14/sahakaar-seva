"""
Mock notification service for SIH prototype
In production, would integrate with SMS, email, push
"""
from typing import List, Dict
from datetime import datetime

class NotificationService:
    def __init__(self):
        self.notifications = []  # In-memory for demo
    
    def send(self, user_id: int, title: str, message: str, type: str = "INFO") -> Dict:
        notif = {
            "id": len(self.notifications) + 1,
            "user_id": user_id,
            "title": title,
            "message": message,
            "type": type,
            "created_at": datetime.now().isoformat(),
            "read": False
        }
        self.notifications.append(notif)
        print(f"[NOTIFICATION] User {user_id}: {title} - {message}")
        return notif
    
    def notify_job_created(self, customer_id: int, job_id: int):
        return self.send(customer_id, "Booking Confirmed", f"Job {job_id} created. Finding verified cooperative workers.", "BOOKING")
    
    def notify_worker_assigned(self, customer_id: int, worker_name: str, job_id: int):
        return self.send(customer_id, "Worker Assigned", f"{worker_name} assigned to job {job_id}. Cooperative verified.", "ASSIGNMENT")
    
    def notify_new_job(self, worker_id: int, job_id: int, service: str):
        return self.send(worker_id, "New Job Opportunity", f"New {service} job {job_id} - Fair distribution via cooperative", "JOB")
    
    def notify_payment(self, worker_id: int, amount: float, total: float):
        return self.send(worker_id, "Payment Received", f"Customer paid ₹{total}. You received ₹{amount}. Transparent settlement.", "PAYMENT")
    
    def notify_cooperative(self, coop_admin_id: int, title: str, message: str):
        return self.send(coop_admin_id, title, message, "COOPERATIVE_ALERT")

# Global instance
notification_service = NotificationService()
