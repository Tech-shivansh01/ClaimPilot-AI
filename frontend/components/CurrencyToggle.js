"use client";

import { useCurrency } from "../lib/CurrencyContext";

export default function CurrencyToggle() {
  const ctx = useCurrency();
  if (!ctx) return null;
  const { currency, toggleCurrency } = ctx;

  return (
    <button className="currency-toggle" onClick={toggleCurrency} title="Switch currency display">
      {currency === "USD" ? "$ USD" : "₹ INR"}
    </button>
  );
}
