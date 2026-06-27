// fixed approximate rate - not pulling live forex, this is just for a demo
// toggle, not a real financial conversion tool
export const USD_TO_INR_RATE = 83;

export function toDisplayAmount(amountUSD, currency) {
  if (currency === "INR") return Math.round(amountUSD * USD_TO_INR_RATE);
  return Math.round(amountUSD);
}

// converts a number the user typed while INR was selected back to the USD
// equivalent, since the backend always stores amounts in USD
export function toBaseUSD(amount, currency) {
  if (currency === "INR") return amount / USD_TO_INR_RATE;
  return amount;
}

export function formatCurrency(amountUSD, currency) {
  if (amountUSD === null || amountUSD === undefined) return "—";
  const symbol = currency === "INR" ? "₹" : "$";
  const display = toDisplayAmount(amountUSD, currency);
  const locale = currency === "INR" ? "en-IN" : "en-US";
  return `${symbol}${display.toLocaleString(locale)}`;
}
