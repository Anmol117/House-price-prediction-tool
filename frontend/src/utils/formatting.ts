/**
 * Currency and number formatting utilities for Indian Real Estate (INR).
 */

/**
 * Format numeric value as Indian Rupee (INR) currency.
 * Example: 8200000 -> "₹82,00,000"
 */
export function formatINR(value: number | string): string {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) {
    return '₹0';
  }

  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(num);
}

/**
 * Format numeric value into Indian Lakh / Crore notation.
 * Examples:
 *   8200000 -> "₹82.00 Lakh"
 *   15000000 -> "₹1.50 Cr"
 *   75000 -> "₹75,000"
 */
export function formatLakhCrore(value: number | string): string {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) {
    return '₹0';
  }

  if (num >= 10000000) {
    const cr = num / 10000000;
    return `₹${cr.toFixed(2)} Cr`;
  } else if (num >= 100000) {
    const lakh = num / 100000;
    return `₹${lakh.toFixed(2)} Lakh`;
  } else {
    return formatINR(num);
  }
}

/**
 * Backward-compatible alias for formatINR.
 */
export function formatCurrency(value: number | string): string {
  return formatINR(value);
}

/**
 * Format a number with Indian grouping separators (e.g. 1,150 sq ft).
 */
export function formatNumber(value: number | string): string {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return '0';
  return new Intl.NumberFormat('en-IN').format(num);
}
