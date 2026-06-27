from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import init_db, SessionLocal
from app import models
from app.routers import claims, policies
from app.config import settings

app = FastAPI(title="ClaimPilot AI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(claims.router)
app.include_router(policies.router)

app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


def seed_demo_policies(db):
    if db.query(models.Policy).count() > 0:
        return  # already seeded, don't duplicate

    # note: deductible isn't a fixed/regulated number anywhere - it's just whatever
    # each policy is written with, varies a lot insurer to insurer. these are just
    # reasonable-looking demo values. since /policies now supports creating your own
    # policy with whatever deductible you want, these only matter for the 2 seed demos
    demo_policies = [
        models.Policy(
            policy_number="POL1001",
            holder_name="Ravi Kumar",
            vehicle_reg_no="UP14AB1234",
            coverage_type="comprehensive",
            coverage_limit=200000,
            deductible=500,
            registered_location="Roorkee, Uttarakhand",
            start_date="2025-01-01",
            end_date="2026-12-31",
        ),
        models.Policy(
            policy_number="POL1002",
            holder_name="Anjali Mehta",
            vehicle_reg_no="DL08CA5678",
            coverage_type="third_party_plus",
            coverage_limit=100000,
            deductible=1000,
            registered_location="New Delhi",
            start_date="2024-06-15",
            end_date="2026-06-14",
        ),
    ]
    db.add_all(demo_policies)
    db.commit()


@app.on_event("startup")
def on_startup():
    init_db()
    db = SessionLocal()
    try:
        seed_demo_policies(db)
    finally:
        db.close()

    if settings.MOCK_MODE:
        print("⚠ running in MOCK MODE - no OPENAI_API_KEY set, AI agents will return placeholder results")


@app.get("/")
def root():
    return {"message": "ClaimPilot AI backend is running", "mock_mode": settings.MOCK_MODE}
