from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel


class PolicyOut(BaseModel):
    id: int
    policy_number: str
    holder_name: str
    vehicle_reg_no: Optional[str] = None
    coverage_type: str
    coverage_limit: float
    deductible: float
    registered_location: Optional[str] = None

    class Config:
        from_attributes = True


class PolicyCreate(BaseModel):
    holder_name: str
    policy_number: Optional[str] = None  # leave blank and we'll generate one for you
    vehicle_reg_no: Optional[str] = None
    coverage_type: str = "comprehensive"  # picks the plan tier - coverage_limit/deductible are set by us, not the user
    registered_location: Optional[str] = None
    start_date: Optional[str] = None  # defaults to today if not given
    end_date: Optional[str] = None  # defaults to one year out if not given


class ClaimCreate(BaseModel):
    policy_number: str
    claimant_name: str
    incident_date: str  # keeping as plain string (YYYY-MM-DD), no point overengineering a date type for this
    incident_location: Optional[str] = None
    description: Optional[str] = None


class ClaimDocumentOut(BaseModel):
    id: int
    doc_type: str
    original_filename: str

    class Config:
        from_attributes = True


class ClaimOut(BaseModel):
    id: int
    policy_number: str
    claimant_name: str
    incident_date: str
    incident_location: Optional[str] = None
    description: Optional[str] = None
    status: str
    vision_result: Optional[Any] = None
    document_result: Optional[Any] = None
    fraud_result: Optional[Any] = None
    settlement_result: Optional[Any] = None
    compliance_explanation: Optional[str] = None
    created_at: datetime
    documents: list[ClaimDocumentOut] = []

    class Config:
        from_attributes = True


class ClaimListOut(BaseModel):
    id: int
    claimant_name: str
    policy_number: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
