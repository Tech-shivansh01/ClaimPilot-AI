const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function getCoverageTiers() {
  const res = await fetch(`${API_URL}/policies/coverage-tiers`, { cache: "no-store" });
  if (!res.ok) throw new Error("couldn't load coverage plans");
  return res.json();
}

export async function createPolicy(data) {
  const res = await fetch(`${API_URL}/policies`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "couldn't create policy");
  }
  return res.json();
}

export async function createClaim(data) {
  const res = await fetch(`${API_URL}/claims`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "couldn't create claim");
  }
  return res.json();
}

export async function uploadDocument(claimId, docType, file) {
  const formData = new FormData();
  formData.append("doc_type", docType);
  formData.append("file", file);

  const res = await fetch(`${API_URL}/claims/${claimId}/documents`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error("file upload failed");
  return res.json();
}

export async function processClaim(claimId) {
  const res = await fetch(`${API_URL}/claims/${claimId}/process`, { method: "POST" });
  if (!res.ok) throw new Error("processing failed");
  return res.json();
}

export async function deleteClaim(claimId) {
  const res = await fetch(`${API_URL}/claims/${claimId}`, { method: "DELETE" });
  if (!res.ok) throw new Error("couldn't delete claim");
  return res.json();
}

export async function getClaims() {
  const res = await fetch(`${API_URL}/claims`, { cache: "no-store" });
  if (!res.ok) throw new Error("couldn't load claims");
  return res.json();
}

export async function getClaim(claimId) {
  const res = await fetch(`${API_URL}/claims/${claimId}`, { cache: "no-store" });
  if (!res.ok) throw new Error("couldn't load claim");
  return res.json();
}
