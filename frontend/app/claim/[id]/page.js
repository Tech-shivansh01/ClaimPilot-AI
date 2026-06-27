"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getClaim, deleteClaim } from "../../../lib/api";
import StatusBadge from "../../../components/StatusBadge";
import { useCurrency } from "../../../lib/CurrencyContext";
import { formatCurrency } from "../../../lib/currency";

export default function ClaimDetail({ params }) {
  const { id } = params;
  const router = useRouter();
  const [claim, setClaim] = useState(null);
  const [error, setError] = useState("");
  const currencyCtx = useCurrency();
  const currency = currencyCtx?.currency || "USD";

  async function handleDelete() {
    if (!confirm(`Delete claim #${id}? This can't be undone.`)) return;
    try {
      await deleteClaim(id);
      router.push("/dashboard");
    } catch (err) {
      alert(err.message || "couldn't delete claim");
    }
  }

  useEffect(() => {
    getClaim(id)
      .then(setClaim)
      .catch((err) => setError(err.message));
  }, [id]);

  if (error) return <div className="container"><div className="error-box">{error}</div></div>;
  if (!claim) return <div className="container"><p>loading...</p></div>;

  const vision = claim.vision_result || {};
  const fraud = claim.fraud_result || {};
  const settlement = claim.settlement_result || {};
  const documents = claim.document_result?.documents || [];

  return (
    <div className="container">
      <div className="narrow">
      <h2 style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <span>Claim #{claim.id} <StatusBadge status={claim.status} /></span>
        <button onClick={handleDelete} className="btn-secondary" style={{ fontSize: "13px", padding: "8px 14px", borderRadius: "7px", cursor: "pointer" }}>
          🗑️ Delete Claim
        </button>
      </h2>
      <p className="note">
        Filed by {claim.claimant_name} • Policy {claim.policy_number} • Incident on {claim.incident_date}
      </p>

      <div className="card">
        <strong>Description</strong>
        <p>{claim.description || "—"}</p>
      </div>

      {claim.status === "submitted" || claim.status === "processing" ? (
        <div className="card">
          <p>This claim hasn't been processed by the AI agents yet.</p>
        </div>
      ) : (
        <>
          <span className="section-title">📷 Vision AI — Damage Assessment</span>
          <div className="card">
            <p>
              <strong>Severity:</strong> {vision.damage_severity} &nbsp;|&nbsp;
              <strong> Estimated repair cost:</strong> {formatCurrency(vision.estimated_repair_cost, currency)}
            </p>
            <p>
              <strong>Parts affected:</strong> {vision.parts_affected?.join(", ") || "none detected"}
            </p>
            {vision.per_photo?.[0]?.mock_mode && (
              <p className="note">(running in mock mode - add an OPENAI_API_KEY for real vision analysis)</p>
            )}
          </div>

          <span className="section-title">📄 Document Extraction</span>
          <div className="card">
            {documents.length === 0 && <p className="note">No FIR/medical/repair documents were uploaded.</p>}
            {documents.map((d, i) => (
              <div key={i} style={{ marginBottom: "10px" }}>
                <strong>{d.doc_type}:</strong> {d.summary}
              </div>
            ))}
          </div>

          <span className="section-title">🕵️ Fraud Check</span>
          <div className="card">
            <p>
              <strong>Risk level:</strong> {fraud.risk_level} ({fraud.fraud_score}/100)
            </p>
            <table>
              <tbody>
                <tr>
                  <td>Image tampering suspected</td>
                  <td>{fraud.checks?.image_tampering?.tampering_suspected ? "yes" : "no"}</td>
                </tr>
                <tr>
                  <td>Location mismatch</td>
                  <td>{fraud.checks?.location_mismatch?.mismatch ? "yes" : "no"}</td>
                </tr>
                <tr>
                  <td>Possible duplicate claim</td>
                  <td>{fraud.checks?.duplicate_claims?.duplicate_suspected ? "yes" : "no"}</td>
                </tr>
                <tr>
                  <td>Anomaly score (claim pattern)</td>
                  <td>{fraud.checks?.anomaly_score}/100</td>
                </tr>
              </tbody>
            </table>
          </div>

          <span className="section-title">💰 Settlement</span>
          <div className={`result-box result-${settlement.status}`}>
            <p style={{ margin: 0 }}>
              <strong>Decision:</strong> {settlement.status} &nbsp;|&nbsp;
              <strong> Payout:</strong> {formatCurrency(settlement.payout_amount, currency)}
            </p>
            <p className="note" style={{ marginBottom: 0 }}>{settlement.reason}</p>
          </div>

          <span className="section-title">💬 Why this decision? (Compliance Agent)</span>
          <div className="card">
            <p>{claim.compliance_explanation}</p>
          </div>
        </>
      )}
      </div>
    </div>
  );
}
