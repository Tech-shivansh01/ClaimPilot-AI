"use client";

import { useState } from "react";

export default function RippleButton({ className = "", children, onClick, disabled, ...props }) {
  const [ripples, setRipples] = useState([]);

  function handleClick(e) {
    if (disabled) return;

    const rect = e.currentTarget.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height) * 2;
    const x = e.clientX - rect.left - size / 2;
    const y = e.clientY - rect.top - size / 2;
    const id = Date.now() + Math.random();

    setRipples((r) => [...r, { id, x, y, size }]);
    setTimeout(() => {
      setRipples((r) => r.filter((rp) => rp.id !== id));
    }, 650);

    if (onClick) onClick(e);
  }

  return (
    <button className={`ripple-btn ${className}`} onClick={handleClick} disabled={disabled} {...props}>
      {children}
      {ripples.map((r) => (
        <span key={r.id} className="ripple" style={{ left: r.x, top: r.y, width: r.size, height: r.size }} />
      ))}
    </button>
  );
}
