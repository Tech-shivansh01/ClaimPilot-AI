"use client";

import Link from "next/link";
import StatusBadge from "./StatusBadge";
import { deleteClaim } from "../lib/api";

export default function ClaimCard({ claim, onDeleted }) {
  async function handleDelete(e) {
    e.preventDefault();
    e.stopPropagation();
    if (!confirm(`Delete claim #${claim.id}? This can't be undone.`)) return;
    try {
      await deleteClaim(claim.id);
      onDeleted?.(claim.id);
    } catch (err) {
      alert(err.message || "couldn't delete claim");
    }
  }

  return (
    <Link href={`/claim/${claim.id}`} style={{ textDecoration: "none", display: "block", marginBottom: "12px" }}>
      <div className="card list-card" style={{ cursor: "pointer" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <strong style={{ color: "var(--heading)" }}>Claim #{claim.id} — {claim.claimant_name}</strong>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <StatusBadge status={claim.status} />
            <button onClick={handleDelete} title="Delete claim" className="delete-btn">🗑️</button>
          </div>
        </div>
        <div className="note">
          Policy: {claim.policy_number} • Filed on {new Date(claim.created_at).toLocaleDateString()}
        </div>
      </div>
    </Link>
  );
}
