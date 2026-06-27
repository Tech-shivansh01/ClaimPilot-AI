"use client";

import { useEffect, useState } from "react";
import { getClaims } from "../../lib/api";
import ClaimCard from "../../components/ClaimCard";

export default function Dashboard() {
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getClaims()
      .then(setClaims)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const counts = {
    total: claims.length,
    approved: claims.filter((c) => c.status === "approved").length,
    rejected: claims.filter((c) => c.status === "rejected").length,
    manual_review: claims.filter((c) => c.status === "manual_review").length,
  };

  function handleDeleted(claimId) {
    setClaims((prev) => prev.filter((c) => c.id !== claimId));
  }

  return (
    <div className="container">
      <h2>My Claims</h2>
      {error && <div className="error-box">{error}</div>}

      {!loading && claims.length > 0 && (
        <div className="stats-row">
          <div className="stat-card">
            <div className="stat-number">{counts.total}</div>
            <div className="stat-label">Total</div>
          </div>
          <div className="stat-card">
            <div className="stat-number" style={{ color: "#1d7a52" }}>{counts.approved}</div>
            <div className="stat-label">Approved</div>
          </div>
          <div className="stat-card">
            <div className="stat-number" style={{ color: "#c0392b" }}>{counts.rejected}</div>
            <div className="stat-label">Rejected</div>
          </div>
          <div className="stat-card">
            <div className="stat-number" style={{ color: "#b8740a" }}>{counts.manual_review}</div>
            <div className="stat-label">In Review</div>
          </div>
        </div>
      )}

      {loading && <p>loading...</p>}
      {!loading && claims.length === 0 && <p className="note">No claims filed yet.</p>}
      {claims.map((c) => (
        <ClaimCard key={c.id} claim={c} onDeleted={handleDeleted} />
      ))}
    </div>
  );
}
