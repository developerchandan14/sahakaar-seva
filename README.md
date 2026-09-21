# Sahakaar Seva — AI-Powered Digital Operating System for Labour Service Cooperatives
**SIH26089 | Cooperative-first, Not Marketplace Clone**

> “Our platform digitizes the entire ecosystem of labour service cooperatives, enabling them to connect verified workers with customers while improving job access, transparency, workforce planning, skill development, and service management.”

---

## 1. Problem

Labour cooperatives may have 500+ skilled workers but lack digital infrastructure.

- Workers work individually: A gets many customers, B gets none, C has no digital presence, D has no insurance
- No verification, no fair distribution, no workforce planning
- Existing platforms (Urban Company clone) optimize for MORE BOOKINGS + MORE COMMISSION + MORE PROFIT (platform-centric)
- Cooperatives need MORE OPPORTUNITIES + FAIR DISTRIBUTION + WORKER DEVELOPMENT + SERVICE QUALITY + WORKER WELFARE

## 2. Solution

**Sahakaar Seva is NOT another Urban Company.**

It is an **AI-powered Digital Operating System for Labour Service Cooperatives**.

Architecture:
```
CUSTOMER
   ↓ (Sahakaar AI - NL to structured)
SAHAKAAR SEVA WEBSITE (Digital OS)
   ↓ (Fair AI Allocation)
LABOUR SERVICE COOPERATIVE (PostgreSQL + Governance)
   ↓ (Verified Members)
MEMBER WORKERS
```

Worker is **NOT merely an employee** of platform. Worker is **member of cooperative**.

Cooperative is **NOT merely commission-taking middleman**. Cooperative manages:
- Worker registration, verification, training, welfare, payments, administration

### Core Differentiator
Traditional matching: “Who has the highest rating?”
Sahakaar Seva: “Who is qualified AND available AND nearby AND reliable AND currently under-allocated?”

## 3. Features

### Customer Portal
- Natural Language Assistant: “Mere ghar mein fan aur switchboard dono kharab hain” → structured services
- Find verified cooperative members (✓ COOP VERIFIED, Insurance, Skill test)
- Transparent payment breakdown
- Book, Pay (mock gateway), Track, Rate, Dispute

### Worker Member View
- Profile as cooperative member (Member ID: FSWC-E-184, Since 2021)
- Availability management
- Incoming jobs via cooperative (fair distribution)
- Earnings transparency: “Customer paid ₹500. You received ₹440 (88%)”
- Training & Welfare: Insurance active, EV charger training recommended by AI
- Opportunity score: Jobs this month 42 vs coop avg 38 → 91/100

### Cooperative OS (Main Showcase)
- **Dashboard**: Total workers 500 (Elec 120, Plum 95, Carp 80, Clean 205), Today's jobs 247, Revenue, Worker earnings
- **Worker Opportunity Intelligence**: Avg jobs/worker, Carpenters 1.7 ⚠ → Investigate
- **Configurable Payment Policy**: Worker 88% + Coop 6% + Platform 6% = 100% validated, stored in DB, not hardcoded. Terms: Customer Payment → Worker Earnings + Cooperative Fee + Platform Costs (not “salary to cooperative”)
- **Direct Payment Model**: Gateway splits directly → Worker ₹440, Coop ₹30, Platform ₹30
- **AI Command Center**: DATA → AI → INSIGHT → COOP DECISION → ACTION

## 4. AI/ML Methodology (Every AI solves real cooperative problem)

### AI 1: Fair Job Allocation (Most Important)
Weights configurable:
- skill_match 30%, availability 15%, distance 10%, experience 10%, rating 10%, reliability 10%, workload_balance 10%, fairness 5%

Prevents qualified workers being ignored because another has slightly higher rating.
Example:
- Worker A: 8 jobs today, Worker B: 2 jobs, Worker C: 0 jobs → System strongly considers B/C if qualified
- Shows WHY: Skill 96%, Availability 100%, Distance 91%, Reliability 92%, Fairness 94% → Final 94.2

### AI 2: Demand Forecasting
- Features: date, day_of_week, month, service, historical demand, seasonality
- Models: RandomForest (practical, explainable)
- Output: NEXT 7 DAYS Electrical +31%, Plumbing +14%, Cleaning +21%, Carpentry -18%
- Insight: “Electrical demand expected +31% → Train 12, Recruit 5, Increase availability”

### AI 3: Training Recommendation
- Inputs: worker skills, experience, historical jobs, forecasted demand, skill shortages, low-rated jobs
- Example: EV Charger demand ↑35%, Current EV-trained 17, Required 29, Shortage 12 → TRAIN 12-15 ELECTRICIANS IN EV CHARGER INSTALLATION
- Shows which workers should receive it

### AI 4: Opportunity Equity Index (0-100)
- Based on Gini coefficient of jobs per worker, per skill, availability, workload, income distribution
- Dashboard: Equity 87/100, Electricians 91, Plumbers 86, Carpenters 62 ⚠, Cleaners 89
- Explanation: “Carpenters receiving 43% fewer jobs than cooperative average”
- Recommendations: Promote carpentry, expand categories, training

### AI 5: Anomaly Detection
- Isolation Forest, lightweight
- Detects: unusual job volume, earnings, reviews, cancellation rates, payment values
- Example: Worker FSWC-E-184 Job volume 3.7× normal daily average → Review allocation
- Flags, NOT accuses

### AI 6: Natural Language Customer Assistant
- Prototype: keyword-based for Hindi/English mix
- Converts “Mere ghar mein fan aur switchboard dono kharab hain” → services: [fan repair, switchboard repair], urgency: normal
- Assists understanding, not replace cooperative governance

**Data Note**: Demo uses synthetic historical data (500 workers, 10k jobs, 12 months). Clearly labeled in UI. Production model will train on anonymized cooperative data.

## 5. Architecture

```
sahakaar-seva/
  frontend/
    index.html (production, API-connected)
    original_prototype.html (source of truth)
    js/api.js (API client)
  backend/
    main.py (FastAPI app)
    config.py, database.py
    models/ (SQLAlchemy: user, cooperative, worker, job, payment, review, training, welfare, dispute, policy)
    schemas/ (Pydantic)
    routes/ (auth, workers, jobs, payments, cooperative, analytics, training)
    services/ (job_assignment, payment_service, verification, notification)
    ml/ (data_generator, job_assignment, demand_forecasting, training_recommendation, anomaly_detection, fairness_engine)
    seed.py
  docs/
  tests/
```

**Stack**: Frontend HTML+Tailwind+JS+Chart.js, Backend Python FastAPI Pydantic SQLAlchemy, DB PostgreSQL (SQLite fallback), Auth JWT + bcrypt + RBAC, AI pandas numpy sklearn, Deployment Vercel/Render.

## 6. Database Design

See `backend/models/` - PostgreSQL tables:
- users (id, name, phone, email, password_hash, role, is_active)
- cooperatives (id, name, registration_number, location, lat, lon)
- workers (id, user_id, coop_id, member_id, primary_skill, secondary_skills JSON, exp, rating, total_jobs, availability, verification, lat/lon, jobs_this_week/month, completion_rate)
- jobs (id, customer_id, coop_id, worker_id, service, sub_service, description, location, price, status, priority, ai_match_score, ai_match_explanation)
- payments (id, job_id, total, worker_amount, coop_amount, platform_amount, percentages, status, transaction_id)
- reviews, training, welfare, disputes, cooperative_policies (worker%, coop%, platform%, must sum 100)

## 7. API Documentation

Full docs at `/docs` (Swagger).

**Auth**:
- POST /auth/register
- POST /auth/login (form)
- GET /auth/me

**Workers**:
- GET /workers?skill=electrician&cooperative_id=1
- GET /workers/{id}
- POST /workers
- PATCH /workers/{id}/availability

**Jobs**:
- POST /jobs (customer creates)
- GET /jobs?customer_id=1&status=CREATED
- POST /jobs/ai/match (Fair AI allocation, explainable)
- POST /jobs/{id}/accept (worker accepts)
- POST /jobs/{id}/complete

**Payments**:
- POST /payments/create?job_id=1
- GET /payments/job/{job_id}
- GET /payments/job/{job_id}/transparency
- GET /payments/cooperative/{id}/policy
- PUT /payments/cooperative/{id}/policy (configurable, validates 100%)

**Cooperative**:
- GET /cooperative/{id}/dashboard (total workers, today's jobs, revenue, equity, avg jobs by skill)
- GET /cooperative/{id}/workers
- GET /cooperative/{id}/analytics

**AI**:
- GET /ai/demand-forecast (next 7 days, recommendations)
- GET /ai/workforce-insights (equity index)
- GET /ai/training-recommendations (gaps)
- GET /ai/anomalies (Isolation Forest)
- POST /ai/natural-language?query=...

## 8. Payment System

Never hardcoded 88/6/6. Stored in `cooperative_policies`.

Example:
```
Customer Payment: ₹500
Worker: 88% = ₹440
Cooperative: 6% = ₹30 (Admin, Training, Verification, Welfare, Insurance)
Platform: 6% = ₹30 (Digital ops, gateway)
Validation: worker+coop+platform = 100%
```
Every payment generates auditable settlement record with transaction_id.

Display:
- Customer: “Customer paid ₹500. Transparent settlement.”
- Worker: “Customer paid ₹500. You received ₹440 (88%). Coop fee ₹30 used for insurance + training.”

Direct Payment Model option: Gateway splits directly → Worker, Coop, Platform. Transparent.

For SIH prototype: Mock gateway labeled DEMO (UPI_MOCK_DEMO).

## 9. Setup Instructions

```bash
# Clone
git clone <repo>
cd sahakaar-seva

# Backend
cd backend
pip install -r ../requirements.txt

# Env
cp ../.env.example ../.env
# Edit DATABASE_URL - use sqlite for local fallback or postgres

# Seed DB (creates 500 workers, 100 customers, 1000 jobs, demo users)
python -m backend.seed
# Or: python backend/seed.py

# Run API
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
# Docs at http://localhost:8000/docs

# Frontend
# Option 1: Open frontend/index.html directly (uses API_BASE http://localhost:8000)
# Option 2: Serve via python
cd frontend
python -m http.server 3000
# Open http://localhost:3000
```

### Demo Credentials (after seed)
- Admin: 9999999999 / admin123 (COOPERATIVE_ADMIN)
- Customer: 8888888888 / customer123
- Worker: 7777777777 / worker123
- All others: demo123

### Environment Variables
See `.env.example`:
- DATABASE_URL (postgresql://... or sqlite:///./sahakaar_seva.db)
- SECRET_KEY (min 32 chars)
- DEFAULT_WORKER_PERCENTAGE, etc.
- CORS_ORIGINS

## 10. Deployment

- Frontend: Vercel/Netlify - set API_BASE env to backend URL
- Backend: Render/Railway - set DATABASE_URL to hosted Postgres
- DB: Supabase/Neon/Railway Postgres
- Keep secrets in env, not in frontend

Docker:
```bash
docker-compose up
```

## 11. Synthetic Data Explanation

Because real cooperative data not available during development, we generate:
- 1 cooperative (Faridabad Skilled Workers Cooperative)
- 500 workers (120 elec, 95 plum, 80 carp, 205 clean) with realistic Indian names, Faridabad locations, skills, ratings
- 100 customers
- 1000+ historical jobs over 12 months with seasonality (electrical high in summer, cleaning high before Diwali)
- Payments, welfare, training records, sample anomaly (worker with 3.7× normal volume)

UI clearly states: “Demo uses synthetic historical data. Production model will train on anonymized cooperative data.”

No fake claims of real-world accuracy.

## 12. Security

- Password hashing bcrypt
- JWT HS256, expiry 1440 min
- RBAC: CUSTOMER, WORKER, COOPERATIVE_ADMIN, SUPER_ADMIN
- Input validation Pydantic
- ORM prevents SQL injection
- CORS configured
- No API keys in frontend
- Audit logs via payment transaction_id

## 13. Limitations & Future

- Mock payment gateway → integrate Razorpay/UPI
- Keyword NL assistant → Indic LLM (Sarvam, etc.)
- No WebSockets yet → polling, can add Socket.io
- No map UI yet → lat/lon stored, can add Leaflet
- SQLite fallback for demo, Postgres for prod
- Training completion not tracked via certificates yet
- Welfare fund accounting simplified

Future:
- Mobile app for workers
- Offline mode for low-connectivity areas
- Cooperative governance voting
- Multi-cooperative federation
- Insurance integration

## 14. SIH Judge Optimization

- **Technical novelty**: Fair AI allocation (not just rating), Equity Index, Configurable transparent payments, Cooperative OS (not marketplace)
- **Social impact**: 500+ workers, fair distribution, welfare, insurance, training → worker development, not exploitation
- **Scalability**: Multi-cooperative, PostgreSQL, modular AI engines
- **Feasibility**: FastAPI + sklearn (no deep learning unless needed), demo mode 2-3 min full flow
- **AI relevance**: Every AI solves cooperative problem, explainable (shows WHY), DATA→AI→INSIGHT→DECISION→BENEFIT
- **Differentiation**: Cooperative is system, AI is intelligence, worker is beneficiary, customer is requester, platform is infrastructure
- **Prototype assumptions labeled**: Demo data, mock gateway

## 15. Final Demo Story (5-7 min)

1. **Problem**: Cooperative has hundreds of workers but no tech. Problem is coordinating WORK, WORKERS, SKILLS, DEMAND, TRAINING, PAYMENTS, WELFARE, QUALITY
2. **Solution**: Sahakaar Seva digitizes cooperative. AI converts operational data into decisions.
3. **Flow**:
   - Customer types Hindi/English → AI understands → structured job
   - AI finds 12 eligible verified workers → scores with 8 factors including fairness → recommends Priya (under-allocated, 1.2 jobs/wk) over Sunil (4.5 jobs/wk) despite slightly lower rating → shows breakdown 94.2 score
   - Booking creates payment: ₹500 → Worker ₹440 (88%) transparent → Transaction ID
   - Worker dashboard: job appears, earnings update
   - Cooperative dashboard: job count 247→248, revenue, equity index, demand forecast Electrical +31% → Train 12
   - Training gaps: EV charger shortage 12 → Recommend workers
   - Anomaly: FSWC-E-184 3.7× volume flagged for review

**One-line for judges**: “Our platform digitizes the entire ecosystem of labour service cooperatives, enabling them to connect verified workers with customers while improving job access, transparency, workforce planning, skill development, and service management.”

---

**Built for cooperative, not for commission.** 🏛️
