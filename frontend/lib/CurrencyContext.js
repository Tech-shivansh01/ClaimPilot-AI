"use client";

import { createContext, useContext, useEffect, useState } from "react";

const CurrencyContext = createContext(null);

export function CurrencyProvider({ children }) {
  const [currency, setCurrency] = useState("USD");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem("claimpilot-currency");
    if (saved) setCurrency(saved);
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted) return;
    localStorage.setItem("claimpilot-currency", currency);
  }, [currency, mounted]);

  function toggleCurrency() {
    setCurrency((c) => (c === "USD" ? "INR" : "USD"));
  }

  return <CurrencyContext.Provider value={{ currency, toggleCurrency }}>{children}</CurrencyContext.Provider>;
}

export function useCurrency() {
  return useContext(CurrencyContext);
}
