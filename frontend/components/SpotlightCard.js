"use client";

export default function SpotlightCard({ children, className = "", style = {}, tilt = true }) {
  function handleMouseMove(e) {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    e.currentTarget.style.setProperty("--mx", `${x}%`);
    e.currentTarget.style.setProperty("--my", `${y}%`);

    if (tilt) {
      const rotateY = ((x - 50) / 50) * 6; // max 6deg
      const rotateX = ((50 - y) / 50) * 6;
      e.currentTarget.style.transform = `perspective(700px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
    }
  }

  function handleMouseLeave(e) {
    if (tilt) {
      e.currentTarget.style.transform = "perspective(700px) rotateX(0deg) rotateY(0deg)";
    }
  }

  return (
    <div
      className={`spotlight-card ${className}`}
      style={style}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      {children}
    </div>
  );
}
