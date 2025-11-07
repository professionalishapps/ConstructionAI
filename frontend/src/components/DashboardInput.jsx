import React, { useState } from 'react';
import { 
  Grid, Paper, Typography, Button, TextField, CircularProgress, 
  Box, Chip, Alert, Divider
} from '@mui/material';
import { PlayArrow } from '@mui/icons-material';

function DashboardInput() {
  const [analyzing, setAnalyzing] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  // Input state
  const [projectData, setProjectData] = useState({
    projectName: 'Downtown Office Complex',
    contractValue: 15000000,
    currentCompletion: 42.5,
    baselineCompletion: 45.0,
    totalDays: 350,
    spentToDate: 6800000,
    latitude: 37.7749,
    longitude: -122.4194
  });

  const handleInputChange = (field, value) => {
    setProjectData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const runAnalysis = async () => {
    try {
      setAnalyzing(true);
      setError(null);

      // Prepare data for API
      const analysisData = {
        project: {
          id: 'INPUT-001',
          name: projectData.projectName,
          location: {
            lat: parseFloat(projectData.latitude),
            lon: parseFloat(projectData.longitude)
          },
          contract_value: parseFloat(projectData.contractValue)
        },
        schedule: {
          baseline_pct_complete: parseFloat(projectData.baselineCompletion),
          actual_pct_complete: parseFloat(projectData.currentCompletion),
          total_days: parseInt(projectData.totalDays),
          days_elapsed: 148,
          days_remaining: 202
        },
        budget: {
          total: parseFloat(projectData.contractValue),
          spent_to_date: parseFloat(projectData.spentToDate),
          committed: parseFloat(projectData.contractValue) * 0.15,
          contingency: parseFloat(projectData.contractValue) * 0.05
        }
      };

      // Call the backend directly
      const response = await fetch('http://localhost:8000/api/v1/analyze-input', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(analysisData)
      });

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.status}`);
      }

      const data = await response.json();
      setResults(data.analysis_results);

    } catch (err) {
      setError(err.message);
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

  return (
    <Grid container spacing={3}>
      {/* Header */}
      <Grid item xs={12}>
        <Paper sx={{ p: 3, bgcolor: 'primary.main', color: 'white' }}>
          <Typography variant="h4" gutterBottom>
            🏗️ Construction AI - Input Mode
          </Typography>
          <Typography variant="body1">
            Enter your project data below and run analysis with all 14 AI agents
          </Typography>
        </Paper>
      </Grid>

      {/* Input Form */}
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>Project Information</Typography>
          <Box component="form" sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              label="Project Name"
              value={projectData.projectName}
              onChange={(e) => handleInputChange('projectName', e.target.value)}
              fullWidth
            />
            <TextField
              label="Contract Value ($)"
              type="number"
              value={projectData.contractValue}
              onChange={(e) => handleInputChange('contractValue', e.target.value)}
              fullWidth
            />
            <TextField
              label="Current Completion (%)"
              type="number"
              value={projectData.currentCompletion}
              onChange={(e) => handleInputChange('currentCompletion', e.target.value)}
              inputProps={{ min: 0, max: 100, step: 0.1 }}
              fullWidth
            />
            <TextField
              label="Baseline Completion (%)"
              type="number"
              value={projectData.baselineCompletion}
              onChange={(e) => handleInputChange('baselineCompletion', e.target.value)}
              inputProps={{ min: 0, max: 100, step: 0.1 }}
              fullWidth
            />
            <TextField
              label="Total Project Days"
              type="number"
              value={projectData.totalDays}
              onChange={(e) => handleInputChange('totalDays', e.target.value)}
              fullWidth
            />
            <TextField
              label="Spent to Date ($)"
              type="number"
              value={projectData.spentToDate}
              onChange={(e) => handleInputChange('spentToDate', e.target.value)}
              fullWidth
            />
          </Box>
        </Paper>
      </Grid>

      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>Location (for Weather Analysis)</Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              label="Latitude"
              type="number"
              value={projectData.latitude}
              onChange={(e) => handleInputChange('latitude', e.target.value)}
              inputProps={{ step: 0.0001 }}
              fullWidth
            />
            <TextField
              label="Longitude"
              type="number"
              value={projectData.longitude}
              onChange={(e) => handleInputChange('longitude', e.target.value)}
              inputProps={{ step: 0.0001 }}
              fullWidth
            />
            <Alert severity="info">
              Default: San Francisco (37.7749, -122.4194)
            </Alert>
          </Box>

          <Divider sx={{ my: 3 }} />

          <Button
            variant="contained"
            color="primary"
            size="large"
            fullWidth
            startIcon={analyzing ? <CircularProgress size={20} color="inherit" /> : <PlayArrow />}
            onClick={runAnalysis}
            disabled={analyzing}
          >
            {analyzing ? 'Analyzing with 14 AI Agents...' : 'Run Complete Analysis'}
          </Button>
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

      {/* Results */}
      {results && results.agents && (
        <>
          {/* Overall Health */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, textAlign: 'center' }}>
              <Typography variant="h6" gutterBottom>Overall Project Health</Typography>
              <Chip 
                label={results.agents.agent_14_risk_mitigation?.overall_health || 'UNKNOWN'}
                color={getHealthColor(results.agents.agent_14_risk_mitigation?.overall_health)}
                sx={{ fontSize: '1.5rem', height: '60px', width: '150px', mb: 2 }}
              />
              <Typography variant="body2" color="text.secondary">
                Analysis completed in {results.total_duration_seconds?.toFixed(2)}s
              </Typography>
            </Paper>
          </Grid>

          {/* Key Metrics */}
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>Key Performance Indicators</Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Schedule Performance (SPI)</Typography>
                  <Typography variant="h5">
                    {results.agents.agent_1_schedule?.spi?.toFixed(3) || 'N/A'}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Cost Performance (CPI)</Typography>
                  <Typography variant="h5">
                    {results.agents.agent_2_cost?.cpi?.toFixed(3) || 'N/A'}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Weather Risk</Typography>
                  <Typography variant="h5">
                    {results.agents.agent_4_weather?.risk_score || 'N/A'}/100
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Estimated Delay</Typography>
                  <Typography variant="h5">
                    {results.agents.agent_4_weather?.estimated_delay_days || 0} days
                  </Typography>
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          {/* AI Recommendations */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                🤖 AI-Generated Recommendations
                {results.agents.agent_14_risk_mitigation?.ollama_used && (
                  <Chip label="Powered by Ollama" size="small" color="primary" sx={{ ml: 1 }} />
                )}
              </Typography>
              {results.agents.agent_14_risk_mitigation?.recommendations?.map((rec) => (
                <Paper key={rec.id} sx={{ p: 2, mb: 2, bgcolor: 'background.default' }}>
                  <Box display="flex" alignItems="flex-start">
                    <Typography sx={{ mr: 1, fontSize: '1.5rem' }}>{rec.icon}</Typography>
                    <Box flex={1}>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                        <Chip label={rec.priority} color={rec.color} size="small" />
                        <Chip label={rec.implementation_effort} variant="outlined" size="small" />
                      </Box>
                      <Typography variant="body1" gutterBottom>
                        <strong>Action:</strong> {rec.action}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        <strong>Expected Impact:</strong> {rec.expected_impact}
                      </Typography>
                    </Box>
                  </Box>
                </Paper>
              ))}
            </Paper>
          </Grid>

          {/* Agent Status Grid */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>14 AI Agents Execution Status</Typography>
              <Grid container spacing={2}>
                {[
                  { id: 1, name: 'Schedule', key: 'agent_1_schedule', icon: '📅' },
                  { id: 2, name: 'Cost', key: 'agent_2_cost', icon: '💰' },
                  { id: 3, name: 'Subcontractors', key: 'agent_3_subcontractor', icon: '👷' },
                  { id: 4, name: 'Weather', key: 'agent_4_weather', icon: '🌦️' },
                  { id: 5, name: 'Supply Chain', key: 'agent_5_supply_chain', icon: '📦' },
                  { id: 6, name: 'Change Orders', key: 'agent_6_change_orders', icon: '📝' },
                  { id: 7, name: 'Productivity', key: 'agent_7_productivity', icon: '⚡' },
                  { id: 8, name: 'Quality', key: 'agent_8_quality', icon: '✅' },
                  { id: 9, name: 'Progress', key: 'agent_9_progress', icon: '📊' },
                  { id: 10, name: 'Cash Flow', key: 'agent_10_cash_flow', icon: '💵' },
                  { id: 11, name: 'Delays', key: 'agent_11_delay_cause', icon: '⏱️' },
                  { id: 12, name: 'Forecast', key: 'agent_12_completion', icon: '🎯' },
                  { id: 13, name: 'Cost EAC', key: 'agent_13_cost_forecast', icon: '📈' },
                  { id: 14, name: 'Mitigation', key: 'agent_14_risk_mitigation', icon: '🛡️' },
                ].map((agent) => {
                  const hasData = results.agents[agent.key];
                  const hasError = hasData?.error;
                  const riskScore = hasData?.risk_score;

                  return (
                    <Grid item xs={6} sm={4} md={3} key={agent.id}>
                      <Paper sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="h4">{agent.icon}</Typography>
                        <Typography variant="caption" display="block" color="text.secondary">
                          Agent {agent.id}
                        </Typography>
                        <Typography variant="body2" gutterBottom><strong>{agent.name}</strong></Typography>
                        {hasError ? (
                          <Chip label="Error" color="error" size="small" />
                        ) : hasData ? (
                          <>
                            <Chip label="Complete" color="success" size="small" />
                            {riskScore !== undefined && (
                              <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
                                Risk: {riskScore}/100
                              </Typography>
                            )}
                          </>
                        ) : (
                          <Chip label="Pending" color="default" size="small" />
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

      {/* Call to Action */}
      {!analyzing && !results && (
        <Grid item xs={12}>
          <Paper sx={{ p: 5, textAlign: 'center', bgcolor: 'background.default' }}>
            <Typography variant="h5" gutterBottom>Ready to Analyze</Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
              Enter your project data above and click "Run Complete Analysis" to execute all 14 AI agents.
            </Typography>
            <Typography variant="body2" color="text.secondary">
              ✅ No database required • ✅ Real-time weather data • ✅ AI recommendations
            </Typography>
          </Paper>
        </Grid>
      )}
    </Grid>
  );
}

export default DashboardInput;

