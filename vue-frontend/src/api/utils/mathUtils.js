// Format numbers as USD or EUR currency
export const formatCurrency = (value, symbol = '$') => {
  if (value == null || value === '') {
    return symbol === '€' ? `0${symbol}` : `${symbol}0`;
  }

  const number = typeof value === 'string' ? parseFloat(value) : value;
  const abs = Math.abs(number);
  let formatted = '';

  if (abs >= 1_000_000_000_000) {
    formatted = `${(number / 1_000_000_000_000).toFixed(1)}T`;
  } else if (abs >= 1_000_000_000) {
    formatted = `${(number / 1_000_000_000).toFixed(1)}B`;
  } else if (abs >= 1_000_000) {
    formatted = `${(number / 1_000_000).toFixed(1)}M`;
  } else if (abs >= 1_000) {
    formatted = `${(number / 1_000).toFixed(1)}K`;
  } else {
    formatted = number.toString();
  }

  // If the symbol is €, place it after the number
  if (symbol === '€') {
    return `${formatted}${symbol}`;
  }

  // Otherwise, place it before (default USD style)
  return `${symbol}${formatted}`;
};


// Severity for deltaTag
export const getSeverity = (value) => {
  if (value > 0) return 'success';
  if (value < 0) return 'danger';
  return 'info';
};

// Format delta value with + for positive numbers
export const formatDelta = (value) => {
  if (value == null || value === '') return '0%';
  return value > 0 ? `+${value}%` : `${value}%`;
};