from fastapi import APIRouter, HTTPException
import os
from dotenv import load_dotenv

load_dotenv()

# Prefer pg8000, fallback to psycopg2
try:
    import pg8000
    DB_DRIVER = 'pg8000'
except Exception:
    try:
        import psycopg2
        DB_DRIVER = 'psycopg2'
    except Exception:
        DB_DRIVER = None

router = APIRouter(prefix="/api")


def get_db_connection():
    if DB_DRIVER == 'pg8000':
        return pg8000.connect(user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), host=os.getenv('DB_HOST', 'localhost'), port=int(os.getenv('DB_PORT', 5432)), database=os.getenv('DB_NAME'))
    elif DB_DRIVER == 'psycopg2':
        return psycopg2.connect(host=os.getenv('DB_HOST', 'localhost'), port=os.getenv('DB_PORT', 5432), dbname=os.getenv('DB_NAME'), user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'))
    else:
        raise RuntimeError('No DB driver available')


@router.get('/projects/current')
def get_current_project():
    """Return sample project and latest daily metric."""
    try:
        conn = get_db_connection()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB connection error: {e}")

    try:
        cur = conn.cursor()
        cur.execute("SELECT project_id, name, type, location_lat, location_lon, contract_value, start_date, planned_completion, current_completion_pct FROM projects WHERE project_id = %s", ('PRJ-2025-001',))
        row = cur.fetchone()
        if not row:
            return {"project": None}
        project = {
            'project_id': row[0],
            'name': row[1],
            'type': row[2],
            'location': {'lat': float(row[3]), 'lon': float(row[4]) if row[4] is not None else None},
            'contract_value': float(row[5]) if row[5] is not None else None,
            'start_date': row[6].isoformat() if row[6] else None,
            'planned_completion': row[7].isoformat() if row[7] else None,
            'current_completion_pct': float(row[8]) if row[8] is not None else None,
        }

        # latest metric
        cur.execute("SELECT date, spi, cpi, actual_pct_complete, cost_variance, schedule_variance_days, weather_risk_score FROM daily_metrics WHERE project_id=%s ORDER BY date DESC LIMIT 1", ('PRJ-2025-001',))
        m = cur.fetchone()
        latest_metric = None
        if m:
            latest_metric = {
                'date': m[0].isoformat() if m[0] else None,
                'spi': float(m[1]) if m[1] is not None else None,
                'cpi': float(m[2]) if m[2] is not None else None,
                'actual_pct_complete': float(m[3]) if m[3] is not None else None,
                'cost_variance': float(m[4]) if m[4] is not None else None,
                'schedule_variance_days': int(m[5]) if m[5] is not None else None,
                'weather_risk_score': int(m[6]) if m[6] is not None else None,
            }

        # simple agent placeholders
        agents = [
            {'name': 'Schedule Variance Analyzer', 'status': 'COMPLETED'},
            {'name': 'Cost Variance Tracker', 'status': 'COMPLETED'},
            {'name': 'Weather Impact Modeler', 'status': 'COMPLETED'},
        ]

        return {
            'project': project,
            'latest_metric': latest_metric,
            'agents': agents,
        }
    finally:
        try:
            cur.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass
