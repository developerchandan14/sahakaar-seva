# API Documentation — Sahakaar Seva

Base URL: `http://localhost:8000` (dev), production URL from env

Swagger UI: `/docs`
ReDoc: `/redoc`

## Authentication

### POST /auth/register
Register new user.

Request:
```json
{
  "name": "Ramesh Kumar",
  "phone": "9876543210",
  "email": "ramesh@example.com",
  "password": "password123",
  "role": "CUSTOMER",
  "location_text": "Sector 15, Faridabad"
}
```

Roles: CUSTOMER, WORKER, COOPERATIVE_ADMIN, SUPER_ADMIN

Response: UserResponse (id, name, phone, email, role, is_active, created_at)

### POST /auth/login
Login with form (OAuth2).

Form fields:
- username: phone (e.g., 9999999999)
- password: admin123

Response:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {...}
}
```

Use `Authorization: Bearer <token>` for protected routes.

### GET /auth/me
Get current user (requires JWT).

---

## Workers

### GET /workers
List workers with filters.

Query params:
- skill: electrician, plumber, carpenter, cleaner
- cooperative_id: 1
- verification_status: VERIFIED, PENDING, etc.
- availability: AVAILABLE, BUSY, OFFLINE, ON_LEAVE
- limit, offset

Response: List[WorkerResponse] with user_name, user_phone enriched.

### GET /workers/{id}
Get single worker.

### POST /workers
Create worker (requires auth, admin).

Body:
```json
{
  "user_id": 1,
  "cooperative_id": 1,
  "primary_skill": "electrician",
  "secondary_skills": ["wiring", "inverter"],
  "experience_years": 5,
  "latitude": 28.4089,
  "longitude": 77.3178
}
```

Auto-generates member_id: FSWC-E-101

### PATCH /workers/{id}/availability
Update availability.

Body:
```json
{"availability_status": "AVAILABLE"}
```

### PUT /workers/{id}
Update worker details.

---

## Jobs

### POST /jobs
Create job (customer).

Body:
```json
{
  "cooperative_id": 1,
  "service": "electrician",
  "sub_service": "switchboard repair",
  "description": "Switchboard repair required",
  "location": "Sector 15, Faridabad",
  "latitude": 28.4089,
  "longitude": 77.3178,
  "price": 500,
  "priority": "NORMAL"
}
```

Response: JobResponse with status CREATED

### GET /jobs
List jobs with filters.

Query: customer_id, worker_id, cooperative_id, status, service, limit, offset

### GET /jobs/{id}
Get job.

### POST /jobs/ai/match
**Fair AI Job Allocation - Core feature**

Body:
```json
{
  "job_id": 1,
  "top_k": 5
}
```

Response:
```json
{
  "job_id": 1,
  "eligible_count": 12,
  "recommended_worker_id": 3,
  "matches": [
    {
      "worker_id": 3,
      "member_id": "FSWC-E-186",
      "name": "Priya Sharma",
      "primary_skill": "electrician",
      "final_score": 94.2,
      "breakdown": {
        "skill_match": 96,
        "availability": 100,
        "distance": 91,
        "experience": 70,
        "rating": 94,
        "reliability": 92,
        "workload_balance": 95,
        "fairness": 94
      },
      "distance_km": 1.2,
      "explanation": "High skill match • Available now • Nearby (1.2km) • Low workload - opportunity balancing"
    }
  ]
}
```

Updates job: ai_match_score, ai_match_explanation, status MATCHING

### POST /jobs/{id}/accept
Worker accepts job.

Body:
```json
{"worker_id": 3}
```

Updates: worker_id, status ACCEPTED, accepted_at, worker jobs_this_week/month, creates payment record, notification.

### POST /jobs/{id}/complete
Complete job.

Updates: status COMPLETED, completed_at, worker total_jobs/completed_jobs, payment status COMPLETED, notification to worker.

### POST /jobs/{id}/cancel
Cancel job.

---

## Payments

### POST /payments/create?job_id=1
Create payment for job (uses active cooperative policy).

Response: PaymentResponse

### GET /payments/{id}
Get payment.

### GET /payments/job/{job_id}
Get payment by job.

### GET /payments/job/{job_id}/transparency
**Transparent payment breakdown**

Response:
```json
{
  "customer_paid": 500,
  "worker_received": 440,
  "worker_percentage": 88,
  "cooperative_received": 30,
  "platform_costs": 30,
  "message_customer": "Customer paid ₹500. Transparent settlement.",
  "message_worker": "Customer paid ₹500. You received ₹440 (88%). Cooperative fee ₹30 used for insurance + training + operations.",
  "breakdown": {
    "worker": "₹440 (88%)",
    "cooperative": "₹30 (6%) - Admin, Training, Verification, Welfare",
    "platform": "₹30 (6%) - Digital ops, gateway"
  }
}
```

### GET /payments/cooperative/{coop_id}/policy
Get active policy.

### PUT /payments/cooperative/{coop_id}/policy
Update policy (admin).

Body:
```json
{
  "worker_percentage": 88,
  "cooperative_percentage": 6,
  "platform_percentage": 6,
  "notes": "Approved by cooperative board"
}
```

Validation: sum must be 100, worker >=50. Deactivates old policies, creates new active.

---

## Cooperative

### GET /cooperative/{id}
Get cooperative details.

### GET /cooperative/{id}/dashboard
**Main showcase**

Response:
```json
{
  "total_workers": 500,
  "total_customers": 100,
  "todays_jobs": 247,
  "completed_jobs": 201,
  "active_jobs": 35,
  "cancelled_jobs": 11,
  "total_revenue": 123500,
  "worker_earnings": 108680,
  "cooperative_earnings": 7410,
  "opportunity_equity": 87,
  "verification_pending": 13,
  "by_skill": {"electrician": 120, "plumber": 95, "carpenter": 80, "cleaner": 205},
  "avg_jobs_per_worker": 3.1,
  "avg_jobs_by_skill": {"electrician": 4.2, "plumber": 3.8, "carpenter": 1.7, "cleaner": 3.2}
}
```

### GET /cooperative/{id}/workers
List workers in cooperative with enriched data.

### GET /cooperative/{id}/jobs
List jobs in cooperative.

### GET /cooperative/{id}/analytics
Analytics: jobs_by_service, daily_revenue last 7 days.

---

## AI Intelligence

### GET /ai/demand-forecast
Demand forecast next 7 days.

Response:
```json
{
  "forecasts": [
    {
      "service": "electrician",
      "current_avg": 12.5,
      "forecast": [15.2, 16.1, 17.0, 16.5, 15.8, 16.2, 16.4],
      "forecast_avg": 16.4,
      "change_percent": 31.2,
      "trend": "increasing",
      "confidence": "medium",
      "recommendation": "Electrical demand expected +31%. Train 12 electricians, recruit 5"
    }
  ],
  "insights": ["⚡ Electrical demand expected +31% → Train 12 electricians"],
  "data_source": "real"
}
```

If <50 jobs, returns demo_forecast() with note synthetic.

### GET /ai/workforce-insights
Opportunity Equity Index.

Response:
```json
{
  "opportunity_equity_index": 87,
  "gini_coefficient": 0.13,
  "overall_avg_jobs": 3.1,
  "skill_equity": {"electrician": 91, "plumber": 86, "carpenter": 62, "cleaner": 89},
  "avg_jobs_by_skill": {"electrician": 4.2, "plumber": 3.8, "carpenter": 1.7, "cleaner": 3.2},
  "under_allocated_skills": [
    {"skill": "carpenter", "avg_jobs": 1.7, "cooperative_avg": 3.1, "diff_percent": 45, "status": "⚠ Under-allocated"}
  ],
  "explanation": ["Carpenters receiving 43% fewer jobs than coop avg"],
  "recommendations": ["Promote carpentry services", "Investigate availability"]
}
```

### GET /ai/training-recommendations
Training gaps.

Response:
```json
{
  "gaps": [
    {
      "skill": "electrician",
      "sub_skill": "EV Charger Installation",
      "current_trained": 17,
      "required": 29,
      "shortage": 12,
      "demand_increase_percent": 35,
      "recommended_action": "TRAIN 12-15 ELECTRICIANS IN EV CHARGER INSTALLATION",
      "reason": "EV demand ↑35%, shortage 12",
      "priority": "HIGH",
      "recommended_workers": [...]
    }
  ]
}
```

### GET /ai/anomalies
Anomaly detection.

Response:
```json
{
  "worker_anomalies": [
    {
      "worker_id": 1,
      "member_id": "FSWC-E-184",
      "skill": "electrician",
      "anomaly_score": -0.42,
      "pattern": "Job volume 3.7× normal daily average (15 vs avg 4.0)",
      "details": {"jobs_this_week": 15, "jobs_this_month": 80},
      "severity": "HIGH",
      "action": "Review allocation algorithm"
    }
  ],
  "job_anomalies": [],
  "total_flagged": 1,
  "note": "Flags are for review, not accusation"
}
```

### POST /ai/natural-language?query=...&cooperative_id=1
Natural Language Assistant.

Query: "Mere ghar mein fan aur switchboard dono kharab hain"

Response:
```json
{
  "original_query": "Mere ghar mein fan aur switchboard dono kharab hain",
  "detected_services": ["electrician"],
  "sub_services": ["electrician repair"],
  "urgency": "normal",
  "estimated_price": 500,
  "structured": {"services": ["electrician"], "urgency": "normal", "description": "..."},
  "next_step": "Finding verified electrician from cooperative",
  "note": "Prototype NLP - keyword based"
}
```

---

## Training

### GET /training?worker_id=1
List trainings.

### GET /training/recommendations?worker_id=1
Get recommended trainings.

### POST /training/enroll?worker_id=1&course=EV Charger&skill=EV charger
Enroll.

### PATCH /training/{id}?status=COMPLETED
Update status.

---

## Health & Demo

### GET /
Root info.

### GET /health
Health check.

### GET /demo/credentials
Demo credentials.

---

## Error Responses

```json
{
  "detail": "Error message"
}
```

Status codes: 400 validation, 401 auth, 404 not found, 422 Pydantic validation.

---

## Data Consistency

All dashboards use same backend data:
- POST /jobs creates job
- POST /jobs/ai/match scores workers from workers table
- POST /jobs/{id}/accept sets worker_id, updates worker jobs_this_week, creates payment
- GET /cooperative/{id}/dashboard aggregates same jobs table
- GET /ai/demand-forecast uses same jobs table
- GET /payments/job/{id} uses same job price and policy

No fake independent UI numbers.

---

## Rate Limiting & Security

- JWT required for POST/PATCH/PUT (except register/login)
- RBAC: Check role in future (currently any active user can create job, but admin needed for policy update)
- CORS configured
- Password hashing bcrypt
- No secrets in frontend

Future: Add rate limiting (slowapi), role checks per route.
