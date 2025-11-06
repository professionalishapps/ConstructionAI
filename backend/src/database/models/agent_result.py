"""
Agent Result Model
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from src.database.base import Base


class AgentResult(Base):
    __tablename__ = "agent_results"

    id = Column(Integer, primary_key=True)
    project_id = Column(String(50), ForeignKey("projects.project_id"))
    session_id = Column(String(50))
    agent_name = Column(String(100))  # cost_variance, weather_impact, subcontractor_score
    status = Column(String(20))  # pending, running, completed, failed
    input_data = Column(JSON)  # Agent input parameters
    output = Column(Text)  # Agent recommendations/analysis
    error = Column(Text, nullable=True)  # Error message if status=failed
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
