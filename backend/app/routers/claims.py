from datetime import datetime
import shutil

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.services.file_storage import save_upload
from app.services import vector_store
from app.agents.pipeline import run_claim_pipeline
from app.config import settings

router = APIRouter(prefix="/claims", tags=["claims"])

ALLOWED_DOC_TYPES = {"photo", "video", "fir", "medical_report", "repair_estimate"}


@router.post("", response_model=schemas.ClaimOut)
def create_claim(payload: schemas.ClaimCreate, db: Session = Depends(get_db)):
    policy = db.query(models.Policy).filter(models.Policy.policy_number == payload.policy_number).first()
    if not policy:
        raise HTTPException(status_code=404, detail=f"no policy found with number {payload.policy_number}")

    claim = models.Claim(
        policy_id=policy.id,
        policy_number=policy.policy_number,
        claimant_name=payload.claimant_name,
        incident_date=payload.incident_date,
        incident_location=payload.incident_location,
        description=payload.description,
        status="submitted",
    )
    db.add(claim)
    db.commit()
    db.refresh(claim)
    return claim


@router.post("/{claim_id}/documents")
def upload_document(
    claim_id: int,
    doc_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if doc_type not in ALLOWED_DOC_TYPES:
        raise HTTPException(status_code=400, detail=f"doc_type must be one of {ALLOWED_DOC_TYPES}")

    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="claim not found")

    saved_path = save_upload(claim_id, file, doc_type)

    doc = models.ClaimDocument(
        claim_id=claim_id,
        doc_type=doc_type,
        file_path=saved_path,
        original_filename=file.filename,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return {"id": doc.id, "doc_type": doc.doc_type, "filename": doc.original_filename}


@router.post("/{claim_id}/process", response_model=schemas.ClaimOut)
def process_claim(claim_id: int, db: Session = Depends(get_db)):
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="claim not found")

    policy = db.query(models.Policy).filter(models.Policy.id == claim.policy_id).first()

    photo_paths = [d.file_path for d in claim.documents if d.doc_type == "photo"]
    document_paths = [{"path": d.file_path, "doc_type": d.doc_type} for d in claim.documents]

    historical_claim_count = (
        db.query(models.Claim)
        .filter(models.Claim.policy_id == policy.id, models.Claim.id != claim.id)
        .count()
    )

    days_since_start = 365
    policy_active = True
    if policy.start_date:
        try:
            start = datetime.fromisoformat(policy.start_date)
            incident = datetime.fromisoformat(claim.incident_date)
            days_since_start = max(0, (incident - start).days)
            if policy.end_date:
                end = datetime.fromisoformat(policy.end_date)
                policy_active = start <= incident <= end
        except ValueError:
            pass  # if dates are weird just go with the defaults above

    claim.status = "processing"
    db.commit()

    initial_state = {
        "claim_id": claim.id,
        "policy_number": claim.policy_number,
        "incident_date": claim.incident_date,
        "incident_location": claim.incident_location or "",
        "description": claim.description or "",
        "photo_paths": photo_paths,
        "document_paths": document_paths,
        "registered_location": policy.registered_location,
        "coverage_limit": policy.coverage_limit,
        "deductible": policy.deductible,
        "policy_active": policy_active,
        "days_since_policy_start": days_since_start,
        "historical_claim_count": historical_claim_count,
        "vision_result": None,
        "document_result": None,
        "fraud_result": None,
        "settlement_result": None,
        "explanation": None,
        "final_status": None,
    }

    result = run_claim_pipeline(initial_state)

    claim.vision_result = result["vision_result"]
    claim.document_result = result["document_result"]
    claim.fraud_result = result["fraud_result"]
    claim.settlement_result = result["settlement_result"]
    claim.compliance_explanation = result["explanation"]
    claim.status = result["final_status"]
    db.commit()
    db.refresh(claim)

    # store this claim's description embedding so future claims can be checked against it
    vector_store.store_claim_embedding(claim.id, claim.description or "")

    return claim


@router.get("", response_model=list[schemas.ClaimListOut])
def list_claims(db: Session = Depends(get_db)):
    return db.query(models.Claim).order_by(models.Claim.created_at.desc()).all()


@router.get("/{claim_id}", response_model=schemas.ClaimOut)
def get_claim(claim_id: int, db: Session = Depends(get_db)):
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="claim not found")
    return claim


@router.delete("/{claim_id}")
def delete_claim(claim_id: int, db: Session = Depends(get_db)):
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="claim not found")

    # ClaimDocument rows cascade-delete automatically, but the actual files on
    # disk don't - clean those up too so uploads/ doesn't just grow forever
    claim_upload_dir = f"{settings.UPLOAD_DIR}/{claim_id}"
    shutil.rmtree(claim_upload_dir, ignore_errors=True)

    db.delete(claim)
    db.commit()
    return {"deleted": True, "claim_id": claim_id}
