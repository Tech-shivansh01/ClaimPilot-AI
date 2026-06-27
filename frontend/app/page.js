"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import PhotoDropzone from "../components/PhotoDropzone";
import SpotlightCard from "../components/SpotlightCard";
import RippleButton from "../components/RippleButton";

const steps = [
  {
    icon: "📷",
    title: "1. Upload",
    text: "Drop in accident photos, the FIR, medical report, or a repair estimate.",
  },
  {
    icon: "🤖",
    title: "2. Vision Agent",
    text: "GPT-4o Vision looks at the damage and estimates severity + repair cost.",
  },
  {
    icon: "🕵️",
    title: "3. Fraud Check",
    text: "Checks for tampered images, duplicate claims, and odd patterns.",
  },
  {
    icon: "💰",
    title: "4. Settlement",
    text: "Calculates payout against your coverage and explains the decision.",
  },
];

const proofStats = [
  { value: "4", label: "AI Agents" },
  { value: "5-Stage", label: "LangGraph Pipeline" },
  { value: "100%", label: "Explainable Decisions" },
  { value: "0", label: "API Key Required (mock mode)" },
];

export default function Home() {
  const router = useRouter();

  return (
    <div>
      {/* ---- full-bleed hero ---- */}
      <section className="hero-full">
        <div className="hero-bg-orbs">
          <span className="orb orb-coral" />
          <span className="orb orb-teal" />
        </div>

        <div className="hero-inner content-width">
          <div className="hero-left">
            <span className="hero-eyebrow">⚡ Agentic claims pipeline · LangGraph + GPT-4o</span>
            <motion.h1 initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
              File a claim, get an <span className="accent">AI-reviewed decision</span> in seconds — not days.
            </motion.h1>
            <motion.p initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.1 }}>
              ClaimPilot AI runs every claim through 4 AI agents — damage detection, document
              extraction, fraud scoring, and settlement — and tells you exactly why it made the
              call it did. Built as a college project to explore agentic pipelines end-to-end.
            </motion.p>

            <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.2 }}>
              <PhotoDropzone />
            </motion.div>

            <div className="hero-cta-row" style={{ marginTop: "18px" }}>
              <RippleButton className="btn-glow" onClick={() => router.push("/submit-claim")}>
                File a Claim Manually
              </RippleButton>
              <RippleButton
                className="btn-glow"
                style={{ background: "transparent", border: "1.5px solid rgba(255,255,255,0.4)" }}
                onClick={() => router.push("/dashboard")}
              >
                View My Claims
              </RippleButton>
            </div>
          </div>

          <motion.div
            className="hero-right"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.15 }}
          >
            <div className="orbit-ring" />
            <div className="orbit-center">🛡️</div>
            <span className="orbit-chip chip-1">📷 Vision</span>
            <span className="orbit-chip chip-2">📄 Docs</span>
            <span className="orbit-chip chip-3">🕵️ Fraud</span>
            <span className="orbit-chip chip-4">💰 Settle</span>
          </motion.div>
        </div>
      </section>

      {/* ---- proof strip ---- */}
      <section className="proof-strip">
        <div className="proof-strip-inner content-width">
          {proofStats.map((s) => (
            <div className="proof-item" key={s.label}>
              <strong>{s.value}</strong>
              <span>{s.label}</span>
            </div>
          ))}
        </div>
      </section>

      {/* ---- rest of the page, normal width ---- */}
      <div className="container">
        <h3 style={{ marginBottom: "4px" }}>How it works</h3>
        <p className="note" style={{ marginBottom: "14px" }}>
          Four agents, chained together with LangGraph, one claim at a time.
        </p>
        <div className="steps-grid">
          {steps.map((s, i) => (
            <motion.div
              key={s.title}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.08 }}
            >
              <SpotlightCard className="step-card">
                <span className="step-icon">{s.icon}</span>
                <h4>{s.title}</h4>
                <p>{s.text}</p>
              </SpotlightCard>
            </motion.div>
          ))}
        </div>

        <div className="demo-banner">
          🧪 Two demo policies are pre-loaded: <code>POL1001</code> and <code>POL1002</code> — or{" "}
          <Link href="/create-policy" style={{ color: "var(--coral)", fontWeight: 600 }}>
            create your own policy
          </Link>{" "}
          with whatever coverage and deductible you want to test.
        </div>
      </div>
    </div>
  );
}
