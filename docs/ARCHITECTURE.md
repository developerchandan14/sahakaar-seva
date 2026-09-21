# Architecture — Sahakaar Seva SIH26089

## Philosophy

**Cooperative is the system, not a feature.**

Most teams build:
```
Customer → Platform → Worker (employee)
Goal: MORE BOOKINGS → MORE COMMISSION → MORE PROFIT
```

We build:
```
Customer → Sahakaar Seva (Digital OS) → Cooperative (Governance) → Member Workers
Goal: MORE OPPORTUNITIES + FAIR DISTRIBUTION + WORKER DEVELOPMENT + WELFARE
```

## System Components

```
┌─────────────────────────────────────────────────────────┐
│                    CUSTOMER LAYER                        │
│  - Natural Language Assistant (Hindi/English)           │
│  - Service selection, location, booking                 │
│  - Transparent payment view                             │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│              SAHAKAAR SEVA - DIGITAL OS                  │
│  Frontend: HTML + Tailwind + JS + Chart.js              │
│  Backend: FastAPI + Pydantic + JWT + RBAC               │
│  - Fair AI Job Allocation Engine (core)                 │
│  - Payment Service (configurable, auditable)            │
│  - Notification Service (mock)                          │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│              COOPERATIVE GOVERNANCE LAYER                │
│  PostgreSQL:                                            │
│  - Cooperatives, Policies (88/6/6 configurable)         │
│  - Workers (member_id, verification, welfare)           │
│  - Jobs, Payments, Reviews, Training, Disputes          │
│  AI Engines:                                            │
│  - Demand Forecasting (RandomForest)                    │
│  - Fairness Engine (Gini → Equity Index)                │
│  - Training Recommender (gap analysis)                  │
│  - Anomaly Detection (Isolation Forest)                 │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│                 MEMBER WORKERS LAYER                     │
│  - Verified members, not employees                      │
│  - Member ID: FSWC-E-184                                │
│  - Skills, availability, workload, rating               │
│  - Earnings transparency, welfare, insurance            │
│  - Training recommendations                             │
└─────────────────────────────────────────────────────────┘
```

## Data Flow - The Intelligence Layer

```
Worker completes job
    ↓
Cooperative system records transaction (PostgreSQL)
    ↓
Worker history updates (total_jobs, jobs_this_week)
    ↓
Demand data updates (service, location, price, time)
    ↓
Cooperative sees trends (Dashboard + AI)
    ↓
AI detects: Electrical +31% next 7 days, Carpenters 1.7 vs 4.2 avg
    ↓
AI recommends: Train 12 electricians, Promote carpentry
    ↓
Cooperative acts: Enrolls workers in training, increases availability
    ↓
Workers receive more opportunities
    ↓
Customers receive better service
```

**This is workforce planning, not just booking.**

## Backend Architecture

### FastAPI App (main.py)
- Creates tables on startup (SQLite fallback, PostgreSQL prod)
- CORS configured via env
- Includes routers: auth, workers, jobs, payments, cooperative, analytics, training

### Database (database.py)
- SQLAlchemy engine, SessionLocal, Base
- Supports both PostgreSQL and SQLite (check_same_thread for SQLite)
- get_db dependency for routes

### Models (SQLAlchemy)
- User: id, name, phone (unique), email, password_hash, role (enum: CUSTOMER, WORKER, COOPERATIVE_ADMIN, SUPER_ADMIN), is_active, location
- Cooperative: id, name, registration_number (unique), description, location, lat/lon, total_members
- Worker: id, user_id (FK unique), cooperative_id (FK), member_id (unique, e.g., FSWC-E-184), primary_skill, secondary_skills (JSON), experience, rating, total_jobs, jobs_this_week/month, availability (enum), verification (enum), lat/lon, completion_rate, insurance_status
- Job: id, customer_id (FK), cooperative_id (FK), worker_id (FK nullable), service, sub_service, description, location, lat/lon, price, status (enum: CREATED, MATCHING, ASSIGNED, ACCEPTED, IN_PROGRESS, COMPLETED, CANCELLED, DISPUTED), priority, ai_match_score, ai_match_explanation (JSON string)
- Payment: id, job_id (FK unique), total, worker_amount, coop_amount, platform_amount, percentages, status, transaction_id (unique), payment_method (UPI_MOCK_DEMO for prototype)
- Review, Training, Welfare, Dispute, CooperativePolicy (worker%, coop%, platform%, approved_by, effective_from, is_active)

### Schemas (Pydantic)
- Validation, request/response models
- WorkerResponse enriches with user_name, user_phone via join

### Routes
- **auth.py**: register, login (OAuth2PasswordRequestForm), login-json, me (JWT dependency)
- **workers.py**: list (filter by skill, coop, verification, availability), get, create (auto member_id), update availability, update
- **jobs.py**: create, list, get, accept (updates worker jobs_this_week, creates payment), complete (updates worker total_jobs, payment status), cancel, ai/match (uses FairJobAssignmentEngine, returns explainable scores)
- **payments.py**: create, get, get by job, transparency (message for customer/worker), get policy, update policy (validates 100%, deactivates old)
- **cooperative.py**: get coop, dashboard (aggregates: total workers, by skill, today's jobs, completed/active/cancelled, revenue today from payments join, verification pending, avg jobs, equity via std/mean), workers, jobs, analytics (jobs by service, daily revenue last 7 days)
- **analytics.py (AI)**: demand-forecast (real data if >50 jobs else demo), workforce-insights (equity), training-recommendations, anomalies, natural-language (keyword-based Hindi/English)
- **training.py**: list, recommendations, enroll, update status

### Services
- **job_assignment.py**: FairJobAssignmentEngine with configurable weights, haversine distance, skill_match, availability, distance_score, experience, rating, reliability (completion_rate + response time), workload_balance (lower current workload = higher score), fairness (fewer total jobs = higher score). Prevents top-rated monopoly. Generates explanation.
- **payment_service.py**: get_active_policy (creates default if none), validate_percentages (sum 100, worker >=50), calculate_split (rounding adjustment), create_payment_for_job, get_transparency_message
- **verification_service.py**: verify_worker, get_pending
- **notification_service.py**: mock in-memory, logs to console, methods for job created, worker assigned, new job, payment, cooperative alerts

### ML Modules
- **data_generator.py**: Generates cooperative, users, workers (120 elec, 95 plum, 80 carp, 205 clean), customers, jobs with seasonality, payments. Uses Faker if available else Indian names list.
- **demand_forecasting.py**: prepare_features (day_of_week, month, is_weekend, days_since_start), forecast_service (RandomForest if >14 days data else avg), forecast_all, get_cooperative_insights, demo_forecast
- **fairness_engine.py**: calculate_gini, calculate_opportunity_equity (Gini → equity 0-100, per-skill equity, avg jobs by skill, under_allocated), generate_explanation, get_recommendations, demo_fairness
- **training_recommendation.py**: emerging_skills map, analyze_skill_gaps (forecast + current trained → shortage), recommend_workers_for_training (score: no emerging skill +40, mid exp +20, low workload +20, high rating +20), demo
- **anomaly_detection.py**: AnomalyDetector with IsolationForest contamination 0.05, detect_worker_anomalies (features: total, week, month, rating, completion_rate), explain_anomaly (3.7× volume, low completion, low rating), detect_job_anomalies (frequent cancellers, unusual pricing), demo with injected anomaly
- **job_assignment.py**: re-exports FairJobAssignmentEngine

## Frontend Architecture

### index.html (Production)
- Preserves original prototype visual identity: off-white #fdfbf7, dark #1a1a18, green #16a34a, rounded cards, Plus Jakarta Sans + IBM Plex Mono
- Adds: API status indicator, demo banner, login modal, backend-connected stats
- Role tabs: customer, worker, coop (coop is main)
- **Customer**: NL assistant textarea → calls /ai/natural-language, service buttons, location/desc/price inputs, create job → calls /jobs + /jobs/ai/match, shows AI matching panel with explainable breakdown (skill, availability, distance, etc.), payment breakdown from configurable policy, confirm → /jobs/{id}/accept + /payments
- **Worker**: Profile card, opportunity vs coop avg, incoming jobs (mock + real), earnings transparency, training recommendations from /ai/training-recommendations
- **Cooperative OS**: 5 stats cards from /cooperative/{id}/dashboard (real API), AI Command Center (4 cards: demand +31%, carpentry 1.7, under-allocated, anomaly), charts (jobs per worker, demand trend) via Chart.js, training gaps from /ai/training-recommendations, anomalies from /ai/anomalies, configurable payment sliders that call PUT /payments/cooperative/{id}/policy, demand forecast list, judge summary
- **API Client (js/api.js)**: class ApiClient with base URL, token from localStorage, request method with Authorization header, methods for auth, workers, jobs, payments, cooperative, AI
- **Demo Mode**: toggle banner, runFullDemo() does NL → createJob → aiMatch → accept → payment → update dashboards in 2-3 min
- **Fallback**: If API offline, uses synthetic mock data, shimmer loading, still demonstrates flow

### original_prototype.html
- Source of truth for product concept, UI structure, terminology, cooperative-first philosophy
- Preserved as reference

## Payment Architecture

### Never Hardcode 88/6/6
Stored in cooperative_policies table, per cooperative, with history.

### Validation
worker + cooperative + platform = 100%, worker >=50%

### Calculation
- total_amount = job.price
- worker_amount = round(total * worker% /100, 2)
- cooperative_amount = round(total * coop% /100, 2)
- platform_amount = round(total * platform% /100, 2)
- Adjust rounding diff to worker_amount

### Settlement Records
Payment table: job_id unique, percentages stored, transaction_id unique (TXN-...), payment_method (UPI_MOCK_DEMO), status

### Transparency
GET /payments/job/{id}/transparency returns:
- customer_paid, worker_received, percentages
- message_customer: "Customer paid ₹500. Transparent settlement."
- message_worker: "Customer paid ₹500. You received ₹440 (88%). Coop fee ₹30 used for insurance + training."
- breakdown with usage: Admin, Training, Verification, Welfare

### Direct Payment Model
Optional: Payment gateway splits directly → Worker ₹440, Coop ₹30, Platform ₹30
Worker sees exactly what customer paid.

## Security

- Password hashing: passlib bcrypt
- JWT: python-jose HS256, expiry 1440 min, secret min 32 chars from env
- RBAC: UserRole enum, get_current_user decodes JWT sub=phone, get_current_active_user checks is_active
- Input validation: Pydantic schemas
- SQL injection protection: SQLAlchemy ORM
- CORS: configurable origins from env
- No secrets in frontend: API_BASE via env, token in localStorage (prototype, prod should use httpOnly cookie)
- Audit: transaction_id, payment records, job status history

## Deployment

- **Frontend**: Vercel/Netlify, set API_BASE to backend URL, static hosting
- **Backend**: Render/Railway, set DATABASE_URL to hosted Postgres, SECRET_KEY from env, uvicorn
- **DB**: Supabase/Neon/Railway Postgres, or local SQLite fallback
- **Docker**: docker-compose.yml with db (postgres:15) and backend (uvicorn --reload)
- **Env separation**: .env.example, .env not committed

## Scalability

- Multi-cooperative: cooperative_id FK everywhere, policies per coop
- Horizontal: FastAPI async, stateless JWT, PostgreSQL connection pooling
- AI: Lightweight sklearn models, no deep learning unless needed, explainable, retrainable on anonymized data
- Future: Add Redis for caching, Celery for background jobs, WebSockets for real-time, Leaflet for maps

## Data Consistency

All dashboards use same backend data:
- Customer books ₹500 job → Job exists in customer dashboard
- Worker dashboard → Job appears (worker_id set on accept)
- Cooperative dashboard → Job count increases (today's jobs query)
- Payment → ₹500 recorded, worker ₹440, coop ₹30, platform ₹30
- Analytics → Job included (jobs_by_service, daily_revenue)
- AI → Demand statistics updated (forecast uses jobs table)

No fake independent UI numbers after backend integration.

## Limitations & Future

See README.
