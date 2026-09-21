# Demo Script — Sahakaar Seva SIH26089 (5-7 minutes)

## Setup (Before Judges Arrive)

1. Backend running:
```bash
cd backend
pip install -r ../requirements.txt
python -m backend.seed  # Creates 500 workers, 100 customers, 1000 jobs
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
# Check http://localhost:8000/docs
```

2. Frontend:
```bash
cd frontend
python -m http.server 3000
# Open http://localhost:3000
```

3. Have ready:
- Browser with frontend open, cooperative tab active
- Second tab with /docs open
- Demo credentials: Admin 9999999999/admin123, Customer 8888888888/customer123

---

## Pitch Structure (5-7 min)

### 0:00-0:30 — Problem (The Trap)

> "Most SIH26089 teams build another Urban Company clone. We didn't. 
> 
> Labour cooperatives already have 500+ skilled workers. Problem is not finding customers. Problem is coordinating WORK, WORKERS, SKILLS, DEMAND, TRAINING, PAYMENTS, WELFARE, QUALITY.
> 
> Normal marketplace goal: MORE BOOKINGS → MORE COMMISSION → MORE PROFIT (platform-centric)
> Our goal: MORE OPPORTUNITIES → FAIR DISTRIBUTION → WORKER DEVELOPMENT → COOPERATIVE SUSTAINABILITY"

Show hero slide: Cooperative is system, AI is intelligence, Worker is beneficiary.

### 0:30-1:00 — Architecture (Correct Model)

Show architecture diagram:

```
50 Electricians + 30 Plumbers + 20 Carpenters
  ↓ Form/Join
LABOUR SERVICE COOPERATIVE (manages verification, training, welfare, payments)
  ↓
SAHAKAAR SEVA WEBSITE (Digital OS)
  ↓
CUSTOMERS
```

> "Worker is NOT employee of platform. Worker is MEMBER of cooperative. Member ID: FSWC-E-184, Since 2021, Verified, Insurance active."

Show cooperative dashboard: 500 members, Faridabad Skilled Workers Cooperative, Govt. Regd.

### 1:00-2:30 — Live Demo: Full Flow (DEMO MODE)

Click **▶ DEMO MODE** → **RUN FULL FLOW**

**Step 1: Customer NL Assistant**
- Type in textarea: "Mere ghar mein inverter wiring required hai, jaldi chahiye"
- Click "Understand Request"
- Show AI converts to: services [electrician], urgency urgent, est ₹500
- Auto-fills form

**Step 2: Create Job + AI Matching**
- Click "Create Job + AI Match"
- Show API calls: POST /jobs → POST /jobs/ai/match
- Show AI Matching Result panel:

> "AI analyzed 12 eligible verified workers. Recommended: Priya Sharma • FSWC-E-186
> Final Score: 94.2
> Breakdown: Skill 96%, Availability 100%, Distance 91% (1.2km), Experience 70%, Rating 94%, Reliability 92%, Workload 95%, Fairness 94%
> Explanation: High skill match • Available now • Nearby • Low workload - opportunity balancing • High fairness - under-allocated"

> "Why Priya, not Sunil who has 5.0 rating? Sunil has 4.5 jobs/week (high workload 45%, fairness 50%) vs Priya 1.2 jobs/week (workload 95%, fairness 94%). System prevents top-rated monopoly. That's fair distribution."

Show other matches with lower scores.

**Step 3: Transparent Payment**
- Show payment breakdown: Customer Payment ₹500 → Worker ₹440 (88%) + Coop ₹30 (6%) + Platform ₹30 (6%)
- Show worker transparency: "Customer paid ₹500. You received ₹440 (88%). Coop fee ₹30 used for insurance + training."
- Show transaction ID: TXN-... • UPI_MOCK_DEMO
- Explain: "Not hardcoded 88/6/6. Configurable per cooperative, stored in DB, validated 100%. Terms: Customer Payment → Worker Earnings + Cooperative Fee + Platform Costs. Much clearer than 'salary to cooperative'. Direct Payment Model: Gateway splits directly → Worker, Coop, Platform."

**Step 4: Confirm Booking**
- Click "CONFIRM & PAY"
- Show: Job accepted, payment settled, worker FSWC-E-186 assigned
- Alert shows full flow explanation

**Step 5: Data Consistency (Critical for Judges)**
- Switch to Worker tab: Show job appears in incoming jobs, earnings transparency updates
- Switch to Cooperative tab: Show today's jobs 247→248, revenue increases, worker earnings update
- Show that everything uses same backend data, no fake numbers

### 2:30-4:00 — Cooperative Command Center (Main Showcase)

> "This is the primary showcase screen. Not customer booking, but cooperative intelligence."

**Stats:**
- Total workers 500 (Elec 120, Plum 95, Carp 80, Clean 205)
- Today's jobs 247, Completed 201, Active 35, Cancelled 11
- Opportunity Equity 87/100, Avg jobs/worker 3.1
- Revenue Today ₹1.2L, Worker earnings ₹1.06L
- Attention: Carpenters 1.7 jobs ⚠ (43% below avg)

**AI Command Center (DATA → AI → DECISION → ACTION):**
- ⚡ Electrical +31% → Train 12 electricians
- 🪚 Carpentry 1.7 jobs → Promote service
- 👷 8 workers under-allocated → Increase exposure
- ⚠ Anomaly FSWC-E-184 Job volume 3.7× normal → Review allocation

> "Worker completes job → System records → Demand updates → Cooperative sees trends → AI recommends → Cooperative acts → Workers get more opportunities → Customers get better service. That's intelligence layer, not booking app."

**Charts:**
- Jobs per worker bar: Electricians 4.2, Plumbers 3.8, Carpenters 1.7 ⚠, Cleaners 3.2 → Cooperative insight: Carpenters need investigation
- Demand trend line: Electrical rising 40% this month, Carpentry declining → Action: Recruit electricians, train members

**Training Gaps:**
- EV Charger demand ↑35%, Current 17, Required 29, Shortage 12 → TRAIN 12-15 ELECTRICIANS IN EV CHARGER INSTALLATION
- Shows which workers should receive it, expected benefit

**Anomaly Detection:**
- Worker FSWC-E-184: Job volume 3.7× normal (15 vs avg 4.0), Score -0.42, HIGH severity
- Action: Review allocation algorithm
- Note: System flags, NOT accuses

**Configurable Payment:**
- Show sliders: Worker 88%, Coop 6%, Platform 6% → Example ₹500 → ₹440, ₹30, ₹30
- Click SAVE AS COOP POLICY → API call PUT /payments/cooperative/1/policy → Validates 100%, stores in DB
- Explain: "Don't call it salary to cooperative. Use transparent terms."

**Demand Forecast:**
- Next 7 days: Electrical +31%, Plumbing +14%, Cleaning +21%, Carpentry -18%
- Each with recommendation

### 4:00-5:00 — Why Different + Tech

> "What makes us different?"

**Traditional:**
- More bookings → More commission → Platform-centric
- Matching: "Who has highest rating?"

**Sahakaar Seva:**
- More opportunities → Fair distribution → Worker development → Cooperative sustainability
- Matching: "Who is qualified AND available AND nearby AND reliable AND under-allocated?"

**Tech Stack:**
- Frontend: HTML Tailwind JS Chart.js (preserves prototype identity, off-white, dark, green)
- Backend: FastAPI Pydantic SQLAlchemy PostgreSQL (SQLite fallback) JWT RBAC
- AI: pandas numpy sklearn RandomForest IsolationForest (no deep learning unless needed, explainable)
- Payment: Configurable, auditable, transaction_id, mock gateway labeled DEMO
- Security: bcrypt, JWT, ORM, CORS, no secrets in frontend
- Deployment: Vercel frontend, Render backend, Supabase Postgres
- Data: Synthetic 500 workers, 100 customers, 1000 jobs, 12 months, seasonality, clearly labeled "Demo uses synthetic data"

**Explainability:**
- Every AI shows WHY: breakdown percentages, distance km, workload, fairness
- Not black box

### 5:00-5:30 — Limitations & Future (Honest)

> "Prototype assumptions, clearly labeled:"

- Mock payment gateway → Razorpay/UPI integration
- Keyword NL assistant → Indic LLM (Sarvam)
- No WebSockets yet → polling, can add
- No map UI yet → lat/lon stored, can add Leaflet
- Welfare accounting simplified

Future: Mobile app for workers, offline mode, cooperative governance voting, multi-cooperative federation, insurance integration

### 5:30-6:00 — One-Line & Close

> "Our platform digitizes the entire ecosystem of labour service cooperatives, enabling them to connect verified workers with customers while improving job access, transparency, workforce planning, skill development, and service management."

> "We are NOT building an online electrician booking website with a chatbot. We are building an AI-powered operating system that helps labour cooperatives manage workers, distribute opportunities fairly, understand demand, plan workforce development, manage transparent settlements, and improve worker welfare."

**Show footer:** "BUILT FOR COOPERATIVE, NOT FOR COMMISSION"

---

## Backup: If API Offline

Frontend has fallback to synthetic mock data:

- AI matching mock with 3 workers, explainable scores
- Demand forecast mock
- Training gaps mock
- Anomaly mock with injected 3.7× volume
- Payment breakdown still works with sliders
- Still demonstrates full flow, just without real DB

Show that system degrades gracefully.

---

## Q&A Preparation

**Q: Why not Urban Company clone?**
A: Show cooperative architecture diagram, member vs employee, fair distribution, welfare, training, configurable payments, equity index. Urban Company optimizes commission, we optimize opportunities.

**Q: How is AI not just buzzword?**
A: Every AI solves cooperative problem: Fair allocation prevents monopoly, Demand forecast helps recruitment, Training gap identifies shortage, Equity measures fairness, Anomaly flags suspicious, NL assists Hindi users. All explainable, DATA→AI→INSIGHT→DECISION→BENEFIT.

**Q: Payment percentages?**
A: Configurable, not hardcoded, stored in cooperative_policies table, validated 100%, worker >=50%. Example 88/6/6 but cooperative approves. Terms: Customer Payment → Worker Earnings + Cooperative Fee + Platform Costs. Direct Payment Model: gateway splits directly. Transparent: worker sees exactly what customer paid.

**Q: Real data?**
A: Demo uses synthetic 500 workers, 100 customers, 1000 jobs, 12 months, seasonality, clearly labeled. Production will train on anonymized cooperative data. No fake accuracy claims.

**Q: Worker is employee?**
A: No, member of cooperative. Member ID FSWC-E-184, Since 2021, Verified, Insurance. Cooperative manages verification, training, welfare, payments, administration. Platform is digital infrastructure.

**Q: Scalability?**
A: Multi-cooperative via cooperative_id FK, policies per coop, PostgreSQL, FastAPI async, stateless JWT, modular AI engines, can add Redis, Celery, WebSockets.

**Q: Security?**
A: bcrypt hashing, JWT HS256, RBAC, Pydantic validation, ORM prevents SQL injection, CORS, no secrets in frontend, transaction_id audit.

---

## Demo Credentials

After `python -m backend.seed`:
- Admin: 9999999999 / admin123 (COOPERATIVE_ADMIN)
- Customer: 8888888888 / customer123
- Worker: 7777777777 / worker123
- Others: demo123

---

## Final Checklist

- [ ] Backend seeded and running on 8000
- [ ] Frontend on 3000, API status shows Online
- [ ] Demo mode toggle works
- [ ] NL assistant works
- [ ] Create job → AI match → payment → confirm works
- [ ] Cooperative dashboard shows real data from API
- [ ] Charts render
- [ ] Training gaps and anomalies load
- [ ] Payment sliders and save policy works
- [ ] /docs open in second tab
- [ ] One-line pitch memorized
