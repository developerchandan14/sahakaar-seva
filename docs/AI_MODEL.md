# AI/ML Documentation — Sahakaar Seva SIH26089

## Principle

> Do not add AI merely because SIH judges expect the word "AI". Every AI feature must solve an actual cooperative problem.

**Core intelligence**: DATA → AI/ML → INSIGHT → COOPERATIVE DECISION → WORKER/CUSTOMER BENEFIT

All models clearly state: "Demo uses synthetic historical data. Production model will train on anonymized cooperative data."

No fabricated claims of real-world accuracy.

---

## 1. Fair AI Job Allocation (Most Important)

### Problem Solved
Traditional platforms select highest-rated worker → top 10% get 80% jobs → others idle → no opportunity equity.

Cooperative goal: FAIR DISTRIBUTION + WORKER DEVELOPMENT + SERVICE QUALITY

### Solution
Scoring engine with 8 factors, configurable weights (sum to 1.0):

```python
DEFAULT_WEIGHTS = {
    "skill_match": 0.30,      # Primary skill = 90, secondary = 60, else 20, bonus if sub_service in secondary
    "availability": 0.15,     # AVAILABLE 100, BUSY 30, OFFLINE 0
    "distance": 0.10,         # Haversine km: 0-2km 100, 5km 90, 10km 70, 20km 50, 50km+ 20
    "experience": 0.10,       # 0yr 40, 5yr 70, 10yr 90, 15+ 100
    "rating": 0.10,           # 0-5 scaled to 0-100
    "reliability": 0.10,      # completion_rate*0.7 + response_time_score*0.3
    "workload_balance": 0.10, # Lower current jobs_this_week than avg = higher score (opportunity balancing)
    "fairness": 0.05          # Fewer total_jobs than avg = higher score (under-allocated boost)
}
```

### Algorithm
1. Get eligible workers: cooperative_id = job.cooperative_id, verification_status = VERIFIED, availability != OFFLINE/ON_LEAVE, primary_skill == service or secondary contains service
2. For each eligible, calculate 8 scores 0-100
3. Final = Σ(score_i * weight_i)
4. Sort descending, top_k
5. Generate explanation: "High skill match • Available now • Nearby (1.2km) • Low workload - opportunity balancing • High fairness - under-allocated"

### Example
- Worker A: 8 jobs today, rating 5.0
- Worker B: 2 jobs today, rating 4.8
- Worker C: 0 jobs today, rating 4.7
- All qualified for switchboard repair
- Traditional: Picks A (5.0 rating)
- Sahakaar: Picks C (fairness 94%, workload 95%) if skill match high → Final 94.2 vs A's 87.5 (because workload 45%, fairness 50%)

### Explainability
Shows breakdown: Skill 96%, Availability 100%, Distance 91%, Experience 70%, Rating 94%, Reliability 92%, Workload 95%, Fairness 94% → Final 94.2
Not black box.

### Code
`backend/services/job_assignment.py` - FairJobAssignmentEngine
- haversine_distance()
- calculate_skill_match(), availability(), distance_score(), experience(), rating(), reliability(), workload_balance(), fairness()
- score_worker(), find_best_workers(), get_eligible_workers()

### Validation
- Test: Create 3 workers with same skill, different jobs_this_week (8,2,0), same rating → system should recommend 0-job worker when skill match equal
- Test: Worker with 0 jobs but low skill should not be recommended over high skill with moderate workload

---

## 2. Demand Forecasting

### Problem Solved
Cooperative doesn't know future demand → can't plan recruitment/training → workers idle or customers wait.

### Solution
Use historical job data (date, day_of_week, month, service, location) to forecast next 7 days per service.

### Features
- date, day_of_week (0-6), month (1-12), day_of_month, is_weekend, days_since_start, service, historical count

### Model
- Start practical: RandomForestRegressor(n_estimators=50, max_depth=8, random_state=42)
- If <14 days data: fallback to simple average
- No deep learning unless clear reason (we have <10k rows, tabular)

### Process
1. Aggregate jobs daily per service: groupby [date, service] count
2. Create time features
3. Train per service model: X = [day_of_week, month, is_weekend, days_since_start], y = count
4. Forecast next 7 days: generate future dates, predict
5. Calculate current_avg (last 14 days), forecast_avg, change_percent = (forecast_avg - current_avg)/current_avg*100
6. Trend: >20% increasing, <-20% decreasing, else stable

### Output Example
```
NEXT 7 DAYS
Electrical: current 12.5/day, forecast 16.4/day, +31%
Plumbing: 8.2 → 9.3, +13%
Cleaning: 10.3 → 12.5, +21%
Carpentry: 6.1 → 5.0, -18%
```

### Operational Recommendations (Auto-generated)
```
AI INSIGHT: Electrical demand expected +31%
Recommended:
→ Train 12 electricians (change%/3)
→ Recruit 5 additional members (change%/10)
→ Increase electrician availability
```

### Code
`backend/ml/demand_forecasting.py` - DemandForecaster
- prepare_features(), forecast_service(), forecast_all(), generate_recommendation(), get_cooperative_insights(), demo_forecast()

### Validation
- Test: Seasonal data with summer electrical spike should forecast higher in Apr-Jun
- Test: Not enough data (<14) should return low confidence

---

## 3. Training Recommendation

### Problem Solved
Skill shortages: EV charger demand ↑ but only 17 trained, need 29 → 12 shortage. Also low-rated workers need quality training.

### Inputs
- Worker skills, experience, historical jobs, customer demand, forecasted demand, skill shortages, failed/low-rated jobs

### Logic
1. For each service, get skilled workers, secondary skill coverage counts
2. Find forecast for service, if change% >15 or shortage:
   - Estimate required workers: forecast_avg *30 / avg_jobs_per_worker
   - Shortage = required - current
   - If shortage >0 or change% >25 → gap
3. Also check low performers: rating <4.0 count >15% of skill group → quality training gap
4. For each gap, recommend specific workers:
   - Score: no emerging skill +40, mid exp 3-10yr +20, low workload ≤3 +20, high rating ≥4.0 +20
   - Sort descending, take shortage+5

### Example
```
EV Charger demand ↑35%
Current EV-trained electricians: 17
Forecast requirement: 29
Potential shortage: 12
AI recommendation: TRAIN 12-15 ELECTRICIANS IN EV CHARGER INSTALLATION
Why: EV demand ↑35%, current 17, required 29, shortage 12
Which workers: List with training_score
Expected benefit: Meet demand, increase worker opportunity
```

### Code
`backend/ml/training_recommendation.py` - TrainingRecommender
- emerging_skills map per service
- analyze_skill_gaps(), recommend_workers_for_training(), demo_training_recommendations()

---

## 4. Opportunity Equity Index

### Problem Solved
Cooperative needs to measure fairness, not just bookings.

### Definition
Score 0-100, 100 = perfect equality, 0 = max inequality. Based on Gini coefficient.

### Calculation
- Gini coefficient: 0 = perfect equality (all workers same jobs), 1 = max inequality (one worker all jobs)
- Formula: Gini = (n+1 -2*Σ(cumsum)/cumsum[-1])/n
- Equity = (1 - Gini)*100

### Per-Skill
- Group workers by primary_skill, calculate Gini per group → skill_equity
- Avg jobs per skill, overall avg
- Under-allocated if avg < overall*0.6 → diff% = (overall-avg)/overall*100

### Dashboard
```
Opportunity Equity: 87/100
Electricians: 91
Plumbers: 86
Carpenters: 62 ⚠
Cleaners: 89
Explanation: "Carpenters receiving 43% fewer jobs than cooperative average (1.7 vs 3.1)"
Possible reasons: Low demand, low visibility, availability, service mismatch, customer awareness
Recommendations: Promote carpentry, expand service categories, offer training, investigate availability
```

### Code
`backend/ml/fairness_engine.py` - FairnessEngine
- calculate_gini(), calculate_opportunity_equity(), generate_explanation(), get_recommendations(), demo_fairness()

---

## 5. Anomaly Detection

### Problem Solved
Detect suspicious patterns without accusing.

### Examples
- Unusual number of jobs assigned to one worker (3.7× normal)
- Sudden extreme earnings
- Repeated identical reviews
- Suspicious cancellation rates (customer cancelled 5+ jobs)
- Abnormal payment values (price 3σ from mean)
- Multiple jobs from suspicious accounts
- Unusual worker activity

### Model
- Isolation Forest, lightweight, unsupervised, contamination 0.05 (5% flagged)
- Features per worker: total_jobs, jobs_this_week, jobs_this_month, rating, completion_rate, earnings_approx
- Fit, decision_function, predict (-1 anomaly, 1 normal)

### Explainability
For each anomaly, generate human-readable reason:
- If jobs_this_week > avg*3 → "Job volume 3.7× normal daily average (15 vs avg 4.0)"
- If completion_rate <0.7 → "Low completion rate 65% - possible quality issue"
- If rating <3.0 and total_jobs >20 → "Low rating 2.8 despite 45 jobs"

### Action
Flag for review, not accusation:
- "Review allocation algorithm - potential fairness issue"
- "Check if worker is overworked or system favoring"
- "Quality review, training recommendation"

### Code
`backend/ml/anomaly_detection.py` - AnomalyDetector
- detect_worker_anomalies(), explain_anomaly(), detect_job_anomalies(), demo_anomalies() with injected anomaly for demo

### Demo Injection
For SIH demo, we inject anomaly: worker 0 has jobs_this_week=15 (normal ~4) → should be flagged as HIGH severity, score -0.42

---

## 6. Natural Language Customer Assistant (Optional)

### Problem Solved
Customer may not know exact service name, may type in Hindi/English mix.

### Example
Input: "Mere ghar mein fan aur switchboard dono kharab hain. Jaldi chahiye."
Output:
```
services: [fan repair, switchboard repair] → electrician
urgency: normal (or urgent if jaldi/emergency)
estimated_price: ₹1000
structured: {services: [electrician], urgency: normal, description: original}
next_step: Finding verified electrician from cooperative
```

### Implementation (Prototype)
- Keyword-based, not LLM (practical for hackathon)
- Keywords map: electrician [fan, switchboard, light, wiring, bijli, pankha], plumber [pipe, leak, nal, paani], etc.
- Urgency: if "urgent, jaldi, emergency, abhi" → urgent, if "kal, tomorrow" → low, else normal
- Price map: electrician 500, plumber 400, carpenter 600, cleaner 800 → sum

### Future
- Production: Indic LLM (Sarvam AI, etc.) for better Hindi/English understanding
- Should assist, not replace cooperative governance

### Code
`backend/routes/analytics.py` - natural_language_assistant()

---

## Data Generator

`backend/ml/data_generator.py` - SahakaarDataGenerator
- Generates 1 cooperative (Faridabad Skilled Workers Cooperative)
- 500 workers: skill distribution 120 elec, 95 plum, 80 carp, 205 clean, Indian names, Faridabad locations, secondary skills, exp, rating, jobs_this_week/month, availability 80% available, verification 97% verified, lat/lon jitter around Faridabad
- 100 customers
- 10k jobs over 12 months with seasonality: electrical high in summer (Apr-Jun 40% weight), cleaning high before Diwali (Oct-Nov 50%), price ranges per service, status 80% completed, 2% cancelled
- Payments: 88/6/6 split
- Clearly labeled synthetic

---

## Explainability Requirement

Every major AI recommendation must show WHY.

Example:
```
Recommended worker: Ramesh Kumar
Skill match: High (96%)
Distance: 1.2 km (91%)
Availability: Available (100%)
Workload: Low (95% - opportunity balancing)
Fairness: High (94% - under-allocated)
Reliability: 94%
Final Score: 94.2
```

Makes system explainable for judges.

---

## Testing

- Fairness: Test that 0-job worker gets boosted over 8-job worker when skill equal
- Demand: Test seasonal spike detection
- Training: Test shortage calculation
- Anomaly: Test injected anomaly flagged
- Payment: Test 100% validation, rounding adjustment

See `tests/` directory.

---

## Limitations & Future

- No deep learning: Not needed for tabular <10k rows, RandomForest is explainable and fast
- Synthetic data: Clearly labeled, production will use anonymized cooperative data
- No real-time retraining: For prototype, models trained on request, production would have scheduled retraining
- No personal data: Uses member_id, not Aadhaar, privacy preserved
- Future: XGBoost/LightGBM, time series models (Prophet), multi-cooperative federated learning
