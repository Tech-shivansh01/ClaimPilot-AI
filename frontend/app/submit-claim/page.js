"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { createClaim, uploadDocument, processClaim } from "../../lib/api";
import { useClaimDraft } from "../../lib/ClaimDraftContext";
import RippleButton from "../../components/RippleButton";

export default function SubmitClaim() {
  const router = useRouter();
  const { draftPhotos, setDraftPhotos } = useClaimDraft();

  const [form, setForm] = useState({
    policy_number: "",
    claimant_name: "",
    incident_date: "",
    incident_location: "",
    description: "",
  });
  const [photos, setPhotos] = useState([]);
  const [fir, setFir] = useState(null);
  const [medicalReport, setMedicalReport] = useState(null);
  const [repairEstimate, setRepairEstimate] = useState(null);

  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState("");
  const [error, setError] = useState("");

  // pick up any photo that was dropped on the landing page
  useEffect(() => {
    if (draftPhotos && draftPhotos.length > 0) {
      setPhotos(draftPhotos);
    }
  }, []);

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      setStep("creating claim...");
      const claim = await createClaim(form);

      if (photos && photos.length > 0) {
        setStep("uploading photos...");
        for (const file of photos) {
          await uploadDocument(claim.id, "photo", file);
        }
      }
      if (fir) {
        setStep("uploading FIR...");
        await uploadDocument(claim.id, "fir", fir);
      }
      if (medicalReport) {
        setStep("uploading medical report...");
        await uploadDocument(claim.id, "medical_report", medicalReport);
      }
      if (repairEstimate) {
        setStep("uploading repair estimate...");
        await uploadDocument(claim.id, "repair_estimate", repairEstimate);
      }

      setStep("running AI agents (vision, fraud check, settlement)...");
      await processClaim(claim.id);

      setDraftPhotos([]); // clear the carried-over draft, claim is filed now
      router.push(`/claim/${claim.id}`);
    } catch (err) {
      setError(err.message || "something went wrong");
      setLoading(false);
      setStep("");
    }
  }

  return (
    <div className="container">
      <div className="narrow">
      <h2>File a New Claim</h2>
      {error && <div className="error-box">{error}</div>}

      <form onSubmit={handleSubmit} className="card">
        <div className="form-section-label">📝 Claim details</div>

        <div className="form-group">
          <label>Policy Number</label>
          <input name="policy_number" value={form.policy_number} onChange={handleChange} placeholder="e.g. POL1001" autoComplete="off" required />
        </div>

        <div className="form-group">
          <label>Your Name</label>
          <input name="claimant_name" value={form.claimant_name} onChange={handleChange} autoComplete="off" required />
        </div>

        <div className="form-group">
          <label>Incident Date</label>
          <input type="date" name="incident_date" value={form.incident_date} onChange={handleChange} required />
        </div>

        <div className="form-group">
          <label>Incident Location</label>
          <input name="incident_location" value={form.incident_location} onChange={handleChange} placeholder="city, state" autoComplete="off" />
        </div>

        <div className="form-group">
          <label>What happened?</label>
          <textarea name="description" rows="3" value={form.description} onChange={handleChange} autoComplete="off" />
        </div>

        <div className="form-section-label">📎 Supporting files</div>

        <div className="form-group">
          <label>
            Accident Photos {photos.length > 0 && <span style={{ color: "var(--teal)" }}>({photos.length} attached)</span>}
          </label>
          <input
            type="file"
            accept="image/*"
            multiple
            onChange={(e) => setPhotos(Array.from(e.target.files))}
          />
          {photos.length > 0 && (
            <div className="dz-preview-row">
              {photos.slice(0, 5).map((file, i) => (
                <img key={i} src={URL.createObjectURL(file)} alt="preview" className="dz-thumb" />
              ))}
            </div>
          )}
        </div>

        <div className="form-group">
          <label>FIR / Police Report (optional)</label>
          <input type="file" onChange={(e) => setFir(e.target.files[0])} />
        </div>

        <div className="form-group">
          <label>Medical Report (optional)</label>
          <input type="file" onChange={(e) => setMedicalReport(e.target.files[0])} />
        </div>

        <div className="form-group">
          <label>Repair Estimate (optional)</label>
          <input type="file" onChange={(e) => setRepairEstimate(e.target.files[0])} />
        </div>

        <RippleButton type="submit" className="btn" disabled={loading}>
          {loading ? "Submitting..." : "Submit Claim"}
        </RippleButton>
        {loading && <p className="note">{step}</p>}
      </form>
      </div>
    </div>
  );
}
