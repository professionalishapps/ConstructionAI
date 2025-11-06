"""
Project Model
"""
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime
from sqlalchemy.sql import func
from src.database.base import Base


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
