import React, { useState, useEffect } from 'react';
import { 
  Grid, Paper, Typography, Button, CircularProgress, Alert, 
  Box, Chip, LinearProgress 
} from '@mui/material';
import { 
  PlayArrow, Refresh, CheckCircle, Warning, Error as ErrorIcon 
} from '@mui/icons-material';
import api from '../../services/api_full';

function DashboardFull() {
  const [projectData, setProjectData] = useState(null);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState(null);

  // Load project data on mount
  useEffect(() => {
    loadProjectData();
  }, []);

  const loadProjectData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.project.getCurrentProject();
      setProjectData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const runAnalysis = async () => {
    if (!projectData?.project?.id) return;

    try {
      setAnalyzing(true);
      setError(null);
      const results = await api.runProjectAnalysis(projectData.project.id);
      setAnalysisResults(results);
    } catch (err) {
      setError(`Analysis failed: ${err.message}`);
    } finally {
      setAnalyzing(false);
    }
  };

  const getHealthColor = (health) => {
    switch (health) {
      case 'GREEN': return 'success';
      case 'YELLOW': return 'warning';
      case 'RED': return 'error';
      default: return 'default';
    }
  };

  const getRiskColor = (score) => {
    if (score < 30) return 'success';
    if (score < 60) return 'warning';
    return 'error';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error && !projectData) {
    return (
      <Alert severity="error" action={
        <Button color="inherit" size="small" onClick={loadProjectData}>
          Retry
        </Button>
      }>
        {error}
      </Alert>
    );
  }

  return (
    <Grid container spacing={3}>
      {/* Header */}
      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Box>
              <Typography variant="h4" gutterBottom>
                🏗️ Construction Risk Monitor - 14 AI Agents
              </Typography>
              <Typography variant="h6" color="text.secondary">
                {projectData?.project?.name || 'No Project Loaded'}
              </Typography>
              {projectData?.project && (
                <Typography variant="body2" color="text.secondary">
                  Project ID: {projectData.project.id} | 
                  Contract Value: ${projectData.project.contract_value?.toLocaleString()} |
                  Completion: {projectData.project.current_completion_pct}%
                </Typography>
              )}
            </Box>
            <Box>
              <Button
                variant="contained"
                color="primary"
                size="large"
                startIcon={analyzing ? <CircularProgress size={20} color="inherit" /> : <PlayArrow />}
                onClick={runAnalysis}
                disabled={analyzing || !projectData?.project}
              >
                {analyzing ? 'Analyzing...' : 'Run 14-Agent Analysis'}
              </Button>
              <Button
                variant="outlined"
                sx={{ ml: 1 }}
                startIcon={<Refresh />}
                onClick={loadProjectData}
                disabled={loading}
              >
                Refresh
              </Button>
            </Box>
          </Box>
        </Paper>
      </Grid>

      {/* Error Display */}
      {error && (
        <Grid item xs={12}>
          <Alert severity="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        </Grid>
      )}

      {/* Current Metrics */}
      {projectData?.latest_metric && (
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Current Performance Metrics</Typography>
            <Grid container spacing={2}>
              <Grid item xs={3}>
                <Typography variant="body2" color="text.secondary">Schedule Performance (SPI)</Typography>
                <Typography variant="h5">{projectData.latest_metric.spi?.toFixed(3) || 'N/A'}</Typography>
                <Chip 
                  label={projectData.latest_metric.spi >= 0.95 ? 'On Track' : 'Behind'} 
                  color={projectData.latest_metric.spi >= 0.95 ? 'success' : 'warning'}
                  size="small"
                />
              </Grid>
              <Grid item xs={3}>
                <Typography variant="body2" color="text.secondary">Cost Performance (CPI)</Typography>
                <Typography variant="h5">{projectData.latest_metric.cpi?.toFixed(3) || 'N/A'}</Typography>
                <Chip 
                  label={projectData.latest_metric.cpi >= 0.95 ? 'On Budget' : 'Over Budget'} 
                  color={projectData.latest_metric.cpi >= 0.95 ? 'success' : 'error'}
                  size="small"
                />
              </Grid>
              <Grid item xs={3}>
                <Typography variant="body2" color="text.secondary">Schedule Variance</Typography>
                <Typography variant="h5">
                  {projectData.latest_metric.schedule_variance_days} days
                </Typography>
              </Grid>
              <Grid item xs={3}>
                <Typography variant="body2" color="text.secondary">Cost Variance</Typography>
                <Typography variant="h5">
                  ${projectData.latest_metric.cost_variance?.toLocaleString() || '0'}
                </Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      )}

      {/* Analysis Results */}
      {analysisResults && (
        <>
          {/* Overall Health */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, textAlign: 'center' }}>
              <Typography variant="h6" gutterBottom>Overall Project Health</Typography>
              <Chip 
                label={analysisResults.overall_health}
                color={getHealthColor(analysisResults.overall_health)}
                sx={{ fontSize: '1.5rem', height: '60px', width: '150px', mb: 2 }}
              />
              <Typography variant="body2" color="text.secondary">
                Analysis completed in {analysisResults.total_duration?.toFixed(2)}s
              </Typography>
              <Typography variant="caption" display="block" color="text.secondary">
                Session: {analysisResults.session_id}
              </Typography>
            </Paper>
          </Grid>

          {/* Top Risks */}
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>🚨 Top Risk Factors</Typography>
              {analysisResults.top_risks?.length > 0 ? (
                analysisResults.top_risks.map((risk, index) => (
                  <Box key={index} sx={{ mb: 2 }}>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Typography variant="body1"><strong>{risk.factor}</strong></Typography>
                      <Chip 
                        label={`${risk.score}/100`}
                        color={getRiskColor(risk.score)}
                        size="small"
                      />
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={risk.score} 
                      color={getRiskColor(risk.score)}
                      sx={{ mt: 1 }}
                    />
                  </Box>
                ))
              ) : (
                <Typography color="text.secondary">No high-risk factors identified</Typography>
              )}
            </Paper>
          </Grid>

          {/* AI Recommendations */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                🤖 AI-Generated Recommendations
                {analysisResults.mitigation?.ollama_used && (
                  <Chip label="Powered by Ollama" size="small" color="primary" sx={{ ml: 1 }} />
                )}
              </Typography>
              {analysisResults.recommendations?.length > 0 ? (
                analysisResults.recommendations.map((rec) => (
                  <Paper key={rec.id} sx={{ p: 2, mb: 2, bgcolor: 'background.default' }}>
                    <Box display="flex" alignItems="flex-start">
                      <Typography sx={{ mr: 1, fontSize: '1.5rem' }}>{rec.icon}</Typography>
                      <Box flex={1}>
                        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                          <Chip label={rec.priority} color={rec.color} size="small" />
                          <Chip label={rec.implementation_effort} variant="outlined" size="small" />
                        </Box>
                        <Typography variant="body1" gutterBottom><strong>Action:</strong> {rec.action}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          <strong>Expected Impact:</strong> {rec.expected_impact}
                        </Typography>
                      </Box>
                    </Box>
                  </Paper>
                ))
              ) : (
                <Typography color="text.secondary">No recommendations available</Typography>
              )}
            </Paper>
          </Grid>

          {/* Executive Summary */}
          {analysisResults.executive_summary && (
            <Grid item xs={12}>
              <Paper sx={{ p: 3, bgcolor: 'primary.light', color: 'primary.contrastText' }}>
                <Typography variant="h6" gutterBottom>📊 Executive Summary</Typography>
                <Typography variant="body1" style={{ whiteSpace: 'pre-line' }}>
                  {analysisResults.executive_summary}
                </Typography>
              </Paper>
            </Grid>
          )}

          {/* Agent Results Grid */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>Agent Execution Results</Typography>
              <Grid container spacing={2}>
                {/* Agent 1-14 Summary Cards */}
                {[
                  { id: 1, name: 'Schedule Variance', key: 'schedule', icon: '📅' },
                  { id: 2, name: 'Cost Variance', key: 'cost', icon: '💰' },
                  { id: 3, name: 'Subcontractors', key: 'subcontractors', icon: '👷' },
                  { id: 4, name: 'Weather Impact', key: 'weather', icon: '🌦️' },
                  { id: 5, name: 'Supply Chain', key: 'supply_chain', icon: '📦' },
                  { id: 6, name: 'Change Orders', key: 'change_orders', icon: '📝' },
                  { id: 7, name: 'Productivity', key: 'productivity', icon: '⚡' },
                  { id: 8, name: 'Quality', key: 'quality', icon: '✅' },
                  { id: 9, name: 'Progress', key: 'progress', icon: '📊' },
                  { id: 10, name: 'Cash Flow', key: 'cash_flow', icon: '💵' },
                  { id: 11, name: 'Delay Causes', key: 'delay_cause', icon: '⏱️' },
                  { id: 12, name: 'Completion Forecast', key: 'completion_forecast', icon: '🎯' },
                  { id: 13, name: 'Cost Forecast', key: 'cost_forecast', icon: '📈' },
                  { id: 14, name: 'Risk Mitigation', key: 'mitigation', icon: '🛡️' },
                ].map((agent) => {
                  const agentData = analysisResults[agent.key];
                  const hasError = agentData?.error;
                  const riskScore = agentData?.risk_score;

                  return (
                    <Grid item xs={6} sm={4} md={3} key={agent.id}>
                      <Paper sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="h4">{agent.icon}</Typography>
                        <Typography variant="caption" display="block" color="text.secondary">
                          Agent {agent.id}
                        </Typography>
                        <Typography variant="body2" gutterBottom><strong>{agent.name}</strong></Typography>
                        {hasError ? (
                          <Chip icon={<ErrorIcon />} label="Error" color="error" size="small" />
                        ) : (
                          <>
                            <Chip icon={<CheckCircle />} label="Complete" color="success" size="small" />
                            {riskScore !== undefined && (
                              <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
                                Risk: {riskScore}/100
                              </Typography>
                            )}
                          </>
                        )}
                      </Paper>
                    </Grid>
                  );
                })}
              </Grid>
            </Paper>
          </Grid>
        </>
      )}

      {/* Call to Action if no analysis */}
      {!analyzing && !analysisResults && projectData?.project && (
        <Grid item xs={12}>
          <Paper sx={{ p: 5, textAlign: 'center', bgcolor: 'background.default' }}>
            <Typography variant="h5" gutterBottom>Ready to Analyze</Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
              Click "Run 14-Agent Analysis" to execute comprehensive risk analysis with all 14 AI agents.
            </Typography>
            <Button
              variant="contained"
              color="primary"
              size="large"
              startIcon={<PlayArrow />}
              onClick={runAnalysis}
            >
              Start Analysis
            </Button>
          </Paper>
        </Grid>
      )}
    </Grid>
  );
}

export default DashboardFull;

