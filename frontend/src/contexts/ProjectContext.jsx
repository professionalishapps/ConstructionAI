/**
 * Project Context
 * Global state management for project data
 */
import { createContext, useContext, useState } from 'react';

const ProjectContext = createContext();

export const useProject = () => {
  const context = useContext(ProjectContext);
  if (!context) {
    throw new Error('useProject must be used within a ProjectProvider');
  }
  return context;
};

export const ProjectProvider = ({ children }) => {
  const [project, setProject] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);

  const value = {
    project,
    setProject,
    metrics,
    setMetrics,
    agents,
    setAgents,
    loading,
    setLoading,
  };

  return (
    <ProjectContext.Provider value={value}>
      {children}
    </ProjectContext.Provider>
  );
};
