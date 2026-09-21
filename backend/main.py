from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from .config import settings, get_cors_origins
from .database import create_tables

# Import routes
from .routes import auth, workers, jobs, payments, cooperative, analytics, training

# Create tables on startup
create_tables()

app = FastAPI(
    title="Sahakaar Seva - Cooperative OS",
    description="""
    **AI-powered Digital Operating System for Labour Service Cooperatives - SIH26089**

    Not a marketplace clone. The cooperative is the system.

    - **Cooperative-first architecture**: Workers are members, not employees
    - **Fair AI Job Allocation**: Prevents top-rated worker from getting all jobs
    - **Transparent Payments**: Configurable split, worker sees exactly what customer paid
    - **Demand Forecasting**: AI predicts demand, recommends training/recruitment
    - **Opportunity Equity**: Measures fairness of job distribution
    - **Anomaly Detection**: Flags suspicious patterns for review

    **Roles**: CUSTOMER, WORKER, COOPERATIVE_ADMIN, SUPER_ADMIN
    """,
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(workers.router)
app.include_router(jobs.router)
app.include_router(payments.router)
app.include_router(cooperative.router)
app.include_router(analytics.router)
app.include_router(training.router)

@app.get("/")
def root():
    return {
        "message": "Sahakaar Seva - Cooperative OS - SIH26089",
        "philosophy": "Cooperative is the system, not a feature",
        "version": "1.0.0",
        "docs": "/docs",
        "demo": "/demo",
        "architecture": "CUSTOMER → SAHAKAAR SEVA → COOPERATIVE → VERIFIED WORKER MEMBERS"
    }

@app.get("/health")
def health():
    return {"status": "healthy", "env": settings.ENV}

@app.get("/demo/credentials")
def demo_credentials():
    return {
        "cooperative_admin": {"phone": "9999999999", "password": "admin123", "role": "COOPERATIVE_ADMIN"},
        "customer": {"phone": "8888888888", "password": "customer123", "role": "CUSTOMER"},
        "worker": {"phone": "7777777777", "password": "worker123", "role": "WORKER"},
        "note": "Run seed script to create demo users. Or use /auth/register"
    }

# Serve frontend if exists
frontend_path = os.path.join(os.path.dirname(__file__), "../../frontend")
if os.path.exists(frontend_path):
    # Will be mounted in production via separate frontend hosting
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
