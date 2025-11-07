from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(String(50), unique=True)
    name = Column(String(200))
    type = Column(String(100))
    location_lat = Column(Numeric(10, 8))
    location_lon = Column(Numeric(11, 8))
    contract_value = Column(Numeric(15, 2))
    start_date = Column(Date)
    planned_completion = Column(Date)
    current_completion_pct = Column(Numeric(5, 2))
    created_at = Column(DateTime, server_default=func.now())

class DailyMetrics(Base):
    __tablename__ = "daily_metrics"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(String(50), ForeignKey("projects.project_id"))
    date = Column(Date)
    spi = Column(Numeric(5, 3))
    cpi = Column(Numeric(5, 3))
    actual_pct_complete = Column(Numeric(5, 2))
    cost_variance = Column(Numeric(15, 2))
    schedule_variance_days = Column(Integer)
    weather_risk_score = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())

class Subcontractor(Base):
    __tablename__ = "subcontractors"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(String(50), ForeignKey("projects.project_id"))
    name = Column(String(200))
    trade = Column(String(100))
    performance_score = Column(Integer)
    on_time_pct = Column(Numeric(5, 2))
    quality_score = Column(Integer)
    safety_incidents = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())

class ChangeOrder(Base):
    __tablename__ = "change_orders"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(String(50), ForeignKey("projects.project_id"))
    co_number = Column(String(50))
    date = Column(Date)
    amount = Column(Numeric(15, 2))
    category = Column(String(100))
    reason = Column(Text)
    status = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())

class Inspection(Base):
    __tablename__ = "inspections"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(String(50), ForeignKey("projects.project_id"))
    date = Column(Date)
    area = Column(String(200))
    inspector = Column(String(100))
    defects_found = Column(Integer)
    severity = Column(String(50))
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

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
    execution_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)