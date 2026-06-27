"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { createPolicy, getCoverageTiers } from "../../lib/api";
import { useCurrency } from "../../lib/CurrencyContext";
import { formatCurrency } from "../../lib/currency";
import RippleButton from "../../components/RippleButton";

export default function CreatePolicy() {
  const router = useRouter();
  const currencyCtx = useCurrency();
  const currency = currencyCtx?.currency || "USD";

  const [tiers, setTiers] = useState(null);
  const [tiersError, setTiersError] = useState("");

  const [form, setForm] = useState({
    holder_name: "",
    policy_number: "",
    vehicle_reg_no: "",
    coverage_type: "comprehensive",
    registered_location: "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [createdPolicy, setCreatedPolicy] = useState(null);

  useEffect(() => {
    getCoverageTiers()
      .then(setTiers)
      .catch((err) => setTiersError(err.message));
  }, []);

  function handleChange(e) {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const payload = { ...form, policy_number: form.policy_number.trim() || null };
      const policy = await createPolicy(payload);
      setCreatedPolicy(policy);
    } catch (err) {
      setError(err.message || "something went wrong");
    } finally {
      setLoading(false);
    }
  }

  if (createdPolicy) {
    return (
      <div className="container">
        <div className="narrow">
        <h2>🎉 Policy Created</h2>
        <div className="card">
          <p>
            Your policy number is <strong style={{ color: "var(--teal)", fontSize: "18px" }}>{createdPolicy.policy_number}</strong>
          </p>
          <p className="note">Save this — you'll need it to file a claim.</p>
          <table>
            <tbody>
              <tr><td>Holder</td><td>{createdPolicy.holder_name}</td></tr>
              <tr><td>Plan</td><td>{tiers?.[createdPolicy.coverage_type]?.label || createdPolicy.coverage_type}</td></tr>
              <tr><td>Coverage limit</td><td>{formatCurrency(createdPolicy.coverage_limit, currency)}</td></tr>
              <tr><td>Deductible</td><td>{formatCurrency(createdPolicy.deductible, currency)}</td></tr>
            </tbody>
          </table>
          <p className="note" style={{ marginTop: "10px" }}>
            Coverage limit and deductible are set automatically by your plan — same as how a
            real insurer prices a policy, not something the policyholder picks.
          </p>
          <RippleButton className="btn" style={{ marginTop: "10px" }} onClick={() => router.push("/submit-claim")}>
            File a Claim With This Policy →
          </RippleButton>
        </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="narrow">
      <h2>Create a Policy</h2>
      <p className="note" style={{ marginBottom: "16px" }}>
        Not using one of the demo policies? Set up your own here. Pick a plan below — coverage
        limit and deductible are set by the plan, the same way a real insurer prices it.
      </p>
      {error && <div className="error-box">{error}</div>}
      {tiersError && <div className="error-box">{tiersError}</div>}

      <form onSubmit={handleSubmit} className="card">
        <div className="form-group">
          <label>Policy Holder Name</label>
          <input name="holder_name" value={form.holder_name} onChange={handleChange} autoComplete="off" required />
        </div>

        <div className="form-group">
          <label>Policy Number (optional — leave blank to auto-generate)</label>
          <input name="policy_number" value={form.policy_number} onChange={handleChange} placeholder="e.g. MYPOLICY1" autoComplete="off" />
        </div>

        <div className="form-group">
          <label>Vehicle Registration Number (optional)</label>
          <input name="vehicle_reg_no" value={form.vehicle_reg_no} onChange={handleChange} placeholder="e.g. UP14AB1234" autoComplete="off" />
        </div>

        <div className="form-group">
          <label>Choose a Plan</label>
          {!tiers && !tiersError && <p className="note">loading plans...</p>}
          {tiers && (
            <div className="plan-grid">
              {Object.entries(tiers).map(([key, tier]) => (
                <div
                  key={key}
                  className={`plan-card ${form.coverage_type === key ? "selected" : ""}`}
                  onClick={() => setForm({ ...form, coverage_type: key })}
                >
                  <h4>{tier.label}</h4>
                  <div className="plan-numbers">
                    {formatCurrency(tier.coverage_limit, currency)} limit · {formatCurrency(tier.deductible, currency)} deductible
                  </div>
                  <p>{tier.description}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="form-group">
          <label>Registered Location (optional)</label>
          <input name="registered_location" value={form.registered_location} onChange={handleChange} placeholder="city, state" autoComplete="off" />
        </div>

        <RippleButton type="submit" className="btn" disabled={loading || !tiers}>
          {loading ? "Creating..." : "Create Policy"}
        </RippleButton>
      </form>
      </div>
    </div>
  );
}
