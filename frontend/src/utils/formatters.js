/**
 * Utility Functions for Formatting
 */

/**
 * Format currency values
 */
export const formatCurrency = (value) => {
  if (value === null || value === undefined) return '$0';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
};

/**
 * Format percentage values
 */
export const formatPercentage = (value, decimals = 1) => {
  if (value === null || value === undefined) return '0%';
  return `${(value * 100).toFixed(decimals)}%`;
};

/**
 * Format dates
 */
export const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

/**
 * Get risk color based on score
 */
export const getRiskColor = (score) => {
  if (score < 30) return 'success';
  if (score < 70) return 'warning';
  return 'error';
};

/**
 * Get status color
 */
export const getStatusColor = (status) => {
  const statusColors = {
    completed: 'success',
    running: 'info',
    pending: 'warning',
    failed: 'error',
  };
  return statusColors[status?.toLowerCase()] || 'default';
};
