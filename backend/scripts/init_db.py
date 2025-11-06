"""Initialize PostgreSQL schema using psycopg2 (avoids SQLAlchemy compatibility issues)."""
import os
from dotenv import load_dotenv
try:
    import pg8000
    DB_DRIVER = 'pg8000'
except Exception:
    try:
        import psycopg2
        DB_DRIVER = 'psycopg2'
    except Exception:
        raise ImportError('No supported Postgres driver found (pg8000 or psycopg2)')

load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'construction_db')
DB_USER = os.getenv('DB_USER', 'admin')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'admin123')

DDL = [
"""
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) UNIQUE,
    name VARCHAR(200),
    type VARCHAR(100),
    location_lat DECIMAL(10,8),
    location_lon DECIMAL(11,8),
    contract_value DECIMAL(15,2),
    start_date DATE,
    planned_completion DATE,
    current_completion_pct DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""",
"""
CREATE TABLE IF NOT EXISTS daily_metrics (
    id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) REFERENCES projects(project_id),
    date DATE,
    spi DECIMAL(5,3),
    cpi DECIMAL(5,3),
    actual_pct_complete DECIMAL(5,2),
    cost_variance DECIMAL(15,2),
    schedule_variance_days INTEGER,
    weather_risk_score INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""",
"""
CREATE TABLE IF NOT EXISTS subcontractors (
    id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) REFERENCES projects(project_id),
    name VARCHAR(200),
    trade VARCHAR(100),
    performance_score INTEGER,
    on_time_pct DECIMAL(5,2),
    quality_score INTEGER,
    safety_incidents INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""",
"""
CREATE TABLE IF NOT EXISTS change_orders (
    id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) REFERENCES projects(project_id),
    co_number VARCHAR(50),
    date DATE,
    amount DECIMAL(15,2),
    category VARCHAR(100),
    reason TEXT,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""",
"""
CREATE TABLE IF NOT EXISTS inspections (
    id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) REFERENCES projects(project_id),
    date DATE,
    area VARCHAR(200),
    inspector VARCHAR(100),
    defects_found INTEGER,
    severity VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""",
"""
CREATE TABLE IF NOT EXISTS agent_results (
    id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) REFERENCES projects(project_id),
    session_id VARCHAR(100),
    agent_name VARCHAR(100),
    status VARCHAR(50),
    output JSONB,
    execution_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""",
]


def main():
    conn = None
    try:
        if DB_DRIVER == 'pg8000':
            conn = pg8000.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=int(DB_PORT), database=DB_NAME)
            cur = conn.cursor()
            for stmt in DDL:
                cur.execute(stmt)
            conn.commit()
            cur.close()
        else:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
            )
            conn.autocommit = True
            cur = conn.cursor()
            for stmt in DDL:
                cur.execute(stmt)
            cur.close()
        print("Schema created/verified successfully")
    except Exception as e:
        print("Error creating schema:", e)
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass

if __name__ == '__main__':
    main()
