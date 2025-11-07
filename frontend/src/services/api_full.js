/**
 * Full API Service with 14-Agent Integration
 */

const API_BASE_URL = 'http://localhost:8000';

// ============================================================================
// PROJECT ENDPOINTS
// ============================================================================

export const projectApi = {
  /**
   * Get list of all projects
   */
  async listProjects() {
    const response = await fetch(`${API_BASE_URL}/api/v1/projects`);
    if (!response.ok) throw new Error('Failed to fetch projects');
    return response.json();
  },

  /**
   * Get detailed project information
   */
  async getProject(projectId) {
    const response = await fetch(`${API_BASE_URL}/api/v1/projects/${projectId}`);
    if (!response.ok) throw new Error('Failed to fetch project');
    return response.json();
  },

  /**
   * Get current/default project (for demo)
   */
  async getCurrentProject() {
    const response = await fetch(`${API_BASE_URL}/api/v1/projects/current`);
    if (!response.ok) throw new Error('Failed to fetch current project');
    return response.json();
  },

  /**
   * Get quick project status
   */
  async getProjectStatus(projectId) {
    const response = await fetch(`${API_BASE_URL}/api/v1/projects/${projectId}/status`);
    if (!response.ok) throw new Error('Failed to fetch project status');
    return response.json();
  }
};

// ============================================================================
// ANALYSIS ENDPOINTS
// ============================================================================

export const analysisApi = {
  /**
   * Run complete 14-agent analysis on a project
   * This is the main analysis endpoint that executes all agents
   */
  async runFullAnalysis(projectId) {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/projects/${projectId}/analyze`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Analysis failed');
    }
    
    return response.json();
  }
};

// ============================================================================
// METRICS ENDPOINTS
// ============================================================================

export const metricsApi = {
  /**
   * Get historical metrics for a project
   */
  async getMetrics(projectId, days = 30) {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/projects/${projectId}/metrics?days=${days}`
    );
    if (!response.ok) throw new Error('Failed to fetch metrics');
    return response.json();
  },

  /**
   * Get change orders for a project
   */
  async getChangeOrders(projectId) {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/projects/${projectId}/change-orders`
    );
    if (!response.ok) throw new Error('Failed to fetch change orders');
    return response.json();
  },

  /**
   * Get quality inspections for a project
   */
  async getInspections(projectId, limit = 50) {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/projects/${projectId}/inspections?limit=${limit}`
    );
    if (!response.ok) throw new Error('Failed to fetch inspections');
    return response.json();
  }
};

// ============================================================================
// SYSTEM ENDPOINTS
// ============================================================================

export const systemApi = {
  /**
   * Check API health
   */
  async healthCheck() {
    const response = await fetch(`${API_BASE_URL}/api/health`);
    if (!response.ok) throw new Error('Health check failed');
    return response.json();
  },

  /**
   * Get system status including agent availability
   */
  async getSystemStatus() {
    const response = await fetch(`${API_BASE_URL}/api/v1/system-status`);
    if (!response.ok) throw new Error('Failed to fetch system status');
    return response.json();
  }
};

// ============================================================================
// CONVENIENCE FUNCTIONS
// ============================================================================

/**
 * Get complete project data for dashboard
 */
export async function getCompleteProjectData(projectId) {
  try {
    const [project, metrics, changeOrders, inspections] = await Promise.all([
      projectApi.getProject(projectId),
      metricsApi.getMetrics(projectId, 30),
      metricsApi.getChangeOrders(projectId),
      metricsApi.getInspections(projectId, 50)
    ]);

    return {
      project: project.project,
      latest_metric: project.latest_metric,
      subcontractors: project.subcontractors,
      metrics: metrics.metrics,
      change_orders: changeOrders.change_orders,
      change_orders_summary: changeOrders.summary,
      inspections: inspections.inspections,
      inspections_summary: inspections.summary
    };
  } catch (error) {
    console.error('Error fetching complete project data:', error);
    throw error;
  }
}

/**
 * Run analysis and get formatted results
 */
export async function runProjectAnalysis(projectId) {
  try {
    const result = await analysisApi.runFullAnalysis(projectId);
    
    if (!result.success) {
      throw new Error('Analysis was not successful');
    }
    
    return {
      session_id: result.analysis_results.session_id,
      agents: result.analysis_results.agents,
      execution_times: result.analysis_results.execution_times,
      total_duration: result.analysis_results.total_duration_seconds,
      timestamp: result.timestamp,
      
      // Extract key results for easy access
      overall_health: result.analysis_results.agents.agent_14_risk_mitigation?.overall_health || 'UNKNOWN',
      recommendations: result.analysis_results.agents.agent_14_risk_mitigation?.recommendations || [],
      executive_summary: result.analysis_results.agents.agent_14_risk_mitigation?.executive_summary || '',
      top_risks: result.analysis_results.agents.agent_14_risk_mitigation?.top_risks || [],
      
      // Individual agent results
      schedule: result.analysis_results.agents.agent_1_schedule,
      cost: result.analysis_results.agents.agent_2_cost,
      subcontractors: result.analysis_results.agents.agent_3_subcontractor,
      weather: result.analysis_results.agents.agent_4_weather,
      supply_chain: result.analysis_results.agents.agent_5_supply_chain,
      change_orders: result.analysis_results.agents.agent_6_change_orders,
      productivity: result.analysis_results.agents.agent_7_productivity,
      quality: result.analysis_results.agents.agent_8_quality,
      progress: result.analysis_results.agents.agent_9_progress,
      cash_flow: result.analysis_results.agents.agent_10_cash_flow,
      delay_cause: result.analysis_results.agents.agent_11_delay_cause,
      completion_forecast: result.analysis_results.agents.agent_12_completion,
      cost_forecast: result.analysis_results.agents.agent_13_cost_forecast,
      mitigation: result.analysis_results.agents.agent_14_risk_mitigation
    };
  } catch (error) {
    console.error('Error running project analysis:', error);
    throw error;
  }
}

export default {
  project: projectApi,
  analysis: analysisApi,
  metrics: metricsApi,
  system: systemApi,
  getCompleteProjectData,
  runProjectAnalysis
};

