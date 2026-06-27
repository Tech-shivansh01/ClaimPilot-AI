import "./globals.css";
import Navbar from "../components/Navbar";
import { ClaimDraftProvider } from "../lib/ClaimDraftContext";
import { ThemeProvider } from "../lib/ThemeContext";
import { CurrencyProvider } from "../lib/CurrencyContext";

export const metadata = {
  title: "ClaimPilot AI",
  description: "AI-assisted insurance claims processing - college project",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="true" />
        <link
          href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Manrope:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <ThemeProvider>
          <CurrencyProvider>
            <ClaimDraftProvider>
              <Navbar />
              {children}
            </ClaimDraftProvider>
          </CurrencyProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
