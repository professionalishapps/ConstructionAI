import React, { useState, useEffect } from 'react';
import { Grid, Paper, Typography } from '@mui/material';
import RiskScoreCard from './RiskScoreCard';
import ProjectTimeline from './ProjectTimeline';
import BudgetTracker from './BudgetTracker';
import WeatherImpact from './WeatherImpact';
import SubcontractorScore from './SubcontractorScore';
import InterventionPanel from './InterventionPanel';
import AgentFlow from './AgentFlow';

function Dashboard() {
  const [projectData, setProjectData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/projects/current');
        const data = await response.json();
        setProjectData(data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching project data:', error);
        setLoading(false);
      }
    };

    fetchData();
    // Poll every 3 seconds
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <Typography>Loading...</Typography>;
  }

  return (
    <Grid container spacing={3}>
      {/* Project Overview */}
      <Grid item xs={12}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h4" gutterBottom>
            Construction Risk Monitor
          </Typography>

          {/* Project summary */}
          <Typography variant="h6">
            {projectData?.project?.name ?? 'Project'}
          </Typography>
          <Typography sx={{ mb: 1 }}>
            Contract: {projectData?.project?.contract_value ? `$${projectData.project.contract_value.toLocaleString()}` : 'N/A'} • Completion: {projectData?.project?.current_completion_pct ?? 'N/A'}%
          </Typography>
          <Typography>
            Latest SPI: {projectData?.latest_metric?.spi ?? 'N/A'} • CPI: {projectData?.latest_metric?.cpi ?? 'N/A'}
          </Typography>
        </Paper>
      </Grid>

      {/* Risk Score and Agent Flow */}
      <Grid item xs={12} md={4}>
        <RiskScoreCard data={projectData?.riskScores} />
      </Grid>
      <Grid item xs={12} md={8}>
        <AgentFlow agents={projectData?.agents} />
      </Grid>

      {/* Timeline and Budget */}
      <Grid item xs={12}>
        <ProjectTimeline data={projectData?.timeline} />
      </Grid>
      <Grid item xs={12} md={6}>
        <BudgetTracker data={projectData?.budget} />
      </Grid>
      <Grid item xs={12} md={6}>
        <WeatherImpact data={projectData?.weather} />
      </Grid>

      {/* Subcontractors and Interventions */}
      <Grid item xs={12}>
        <SubcontractorScore data={projectData?.subcontractors} />
      </Grid>
      <Grid item xs={12}>
        <InterventionPanel data={projectData?.interventions} />
      </Grid>
    </Grid>
  );
}

export default Dashboard;