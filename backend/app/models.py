from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship

from app.database import Base


class Policy(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    policy_number = Column(String, unique=True, index=True, nullable=False)
    holder_name = Column(String, nullable=False)
    vehicle_reg_no = Column(String, nullable=True)
    coverage_type = Column(String, default="comprehensive")
    coverage_limit = Column(Float, default=100000)
    deductible = Column(Float, default=2000)
    registered_location = Column(String, nullable=True)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)

    claims = relationship("Claim", back_populates="policy")


class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("policies.id"))
    policy_number = Column(String, index=True)

    claimant_name = Column(String, nullable=False)
    incident_date = Column(String, nullable=False)
    incident_location = Column(String, nullable=True)
    description = Column(Text, nullable=True)

    status = Column(String, default="submitted")
    # submitted -> processing -> approved / rejected / manual_review

    vision_result = Column(JSON, nullable=True)
    document_result = Column(JSON, nullable=True)
    fraud_result = Column(JSON, nullable=True)
    settlement_result = Column(JSON, nullable=True)
    compliance_explanation = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    policy = relationship("Policy", back_populates="claims")
    documents = relationship("ClaimDocument", back_populates="claim", cascade="all, delete-orphan")


class ClaimDocument(Base):
    __tablename__ = "claim_documents"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id"))
    doc_type = Column(String)  # photo, video, fir, medical_report, repair_estimate
    file_path = Column(String)
    original_filename = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    claim = relationship("Claim", back_populates="documents")
