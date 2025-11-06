/**
 * Application Constants
 */

export const POLLING_INTERVAL = 3000; // 3 seconds

export const AGENT_STATUS = {
  PENDING: 'pending',
  RUNNING: 'running',
  COMPLETED: 'completed',
  FAILED: 'failed',
};

export const RISK_LEVELS = {
  LOW: { min: 0, max: 30, label: 'Low Risk', color: 'success' },
  MEDIUM: { min: 30, max: 70, label: 'Medium Risk', color: 'warning' },
  HIGH: { min: 70, max: 100, label: 'High Risk', color: 'error' },
};

export const API_ENDPOINTS = {
  CURRENT_PROJECT: '/api/v1/projects/current',
  HEALTH: '/api/v1/health',
};
