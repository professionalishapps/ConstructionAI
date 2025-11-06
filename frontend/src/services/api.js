import axios from 'axios';

const BASE_URL = 'http://localhost:8000/api';

const api = {
  // Project endpoints
  getCurrentProject: () => axios.get(`${BASE_URL}/projects/current`),
  getProjectById: (id) => axios.get(`${BASE_URL}/projects/${id}`),
  
  // Metrics endpoints
  getDailyMetrics: (projectId) => axios.get(`${BASE_URL}/projects/${projectId}/metrics`),
  
  // Agent endpoints
  getAgentStatus: (projectId) => axios.get(`${BASE_URL}/projects/${projectId}/status`),
  
  // Weather endpoints
  getWeatherForecast: (projectId) => axios.get(`${BASE_URL}/projects/${projectId}/weather`),
  
  // Risk endpoints
  getRiskScores: (projectId) => axios.get(`${BASE_URL}/projects/${projectId}/risks`),
  
  // Subcontractor endpoints
  getSubcontractors: (projectId) => axios.get(`${BASE_URL}/projects/${projectId}/subcontractors`),
};

export default api;