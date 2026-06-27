import Link from "next/link";
import ThemeToggle from "./ThemeToggle";
import CurrencyToggle from "./CurrencyToggle";

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-inner content-width">
        <span className="brand">
          <span className="logo-emoji">🛡️</span> ClaimPilot AI
        </span>
        <Link href="/">Home</Link>
        <Link href="/dashboard">My Claims</Link>
        <Link href="/create-policy">New Policy</Link>
        <Link href="/submit-claim">File a Claim</Link>
        <CurrencyToggle />
        <ThemeToggle />
      </div>
    </nav>
  );
}
