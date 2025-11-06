"""
Daily Metrics Model
"""
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from src.database.base import Base


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
