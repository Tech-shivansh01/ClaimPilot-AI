import random
import string
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.coverage_tiers import COVERAGE_TIERS, DEFAULT_TIER

router = APIRouter(prefix="/policies", tags=["policies"])


def _generate_unique_policy_number(db: Session) -> str:
    while True:
        candidate = "POL" + "".join(random.choices(string.digits, k=4))
        exists = db.query(models.Policy).filter(models.Policy.policy_number == candidate).first()
        if not exists:
            return candidate


@router.post("", response_model=schemas.PolicyOut)
def create_policy(payload: schemas.PolicyCreate, db: Session = Depends(get_db)):
    """lets anyone spin up their own demo policy instead of being stuck with
    the 2 hardcoded seed ones - generates a policy number if you don't pick one.
    coverage_limit/deductible are NOT taken from the user - they're assigned
    based on the plan tier they pick, same as how a real insurer would set them"""
    if payload.policy_number:
        policy_number = payload.policy_number.strip().upper()
        existing = db.query(models.Policy).filter(models.Policy.policy_number == policy_number).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"policy number {policy_number} is already taken, try another")
    else:
        policy_number = _generate_unique_policy_number(db)

    tier_key = payload.coverage_type if payload.coverage_type in COVERAGE_TIERS else DEFAULT_TIER
    tier = COVERAGE_TIERS[tier_key]

    start_date = payload.start_date or date.today().isoformat()
    end_date = payload.end_date or (date.today() + timedelta(days=365)).isoformat()

    policy = models.Policy(
        policy_number=policy_number,
        holder_name=payload.holder_name,
        vehicle_reg_no=payload.vehicle_reg_no,
        coverage_type=tier_key,
        coverage_limit=tier["coverage_limit"],
        deductible=tier["deductible"],
        registered_location=payload.registered_location,
        start_date=start_date,
        end_date=end_date,
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


@router.get("/coverage-tiers")
def get_coverage_tiers():
    """so the frontend can render the plan options without duplicating these numbers"""
    return COVERAGE_TIERS


@router.get("/{policy_number}", response_model=schemas.PolicyOut)
def get_policy(policy_number: str, db: Session = Depends(get_db)):
    policy = db.query(models.Policy).filter(models.Policy.policy_number == policy_number).first()
    if not policy:
        raise HTTPException(status_code=404, detail="policy not found")
    return policy


@router.get("", response_model=list[schemas.PolicyOut])
def list_policies(db: Session = Depends(get_db)):
    return db.query(models.Policy).all()
